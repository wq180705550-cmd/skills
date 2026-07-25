#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文案虾 — 成品归档与索引脚本 (deterministic)

将成文的各平台版本持久化到「文案虾/成品/<平台>/<日期>-<slug>.md」，
并维护「文案虾/索引.md」内容索引，支持版本管理
（同选题同平台重复成文时，版本号递增 v1→v2→…）。

仅依赖标准库。base 路径可配置，默认 ./文案虾/成品/。
"""

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

DEFAULT_BASE = Path.cwd() / "文案虾" / "成品"
VALID_PLATFORMS = {"公众号", "小红书", "知乎", "今日头条"}


def _slugify(text: str) -> str:
    cleaned = re.sub(r"[^\w一-鿿]+", "-", text.strip()).strip("-")
    return (cleaned[:40] or "article").lower()


def _now_iso() -> str:
    return dt.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def _validate(article: dict) -> None:
    if "title" not in article or not str(article["title"]).strip():
        raise ValueError("成文缺少必填字段 title")
    p = article.get("platform")
    if p not in VALID_PLATFORMS:
        raise ValueError(f"platform 必须是 {VALID_PLATFORMS} 之一，收到: {p}")


def _to_markdown(article: dict, version: int) -> str:
    title = article["title"]
    lines = [
        f"# {title}",
        "",
        f"- **平台**: {article.get('platform', '')}",
        f"- **来源选题**: {article.get('source_topic', '')}",
        f"- **版本**: v{version}",
        f"- **创建时间**: {article.get('created_at', _now_iso())}",
        f"- **slug**: {article.get('slug', '')}",
        "",
        "## 正文",
        "",
        article.get("body", ""),
        "",
    ]
    return "\n".join(lines)


def _field(text: str, name: str):
    m = re.search(rf"-\s*\*\*{name}\*\*\s*:\s*(.+)", text)
    return m.group(1).strip() if m else ""


def _parse_article(md: Path) -> dict:
    text = md.read_text(encoding="utf-8")
    title = text.split("\n", 1)[0].lstrip("# ").strip() if text.startswith("# ") else ""
    ver = _field(text, "版本").lstrip("v") or "1"
    return {
        "title": title,
        "platform": _field(text, "平台"),
        "source_topic": _field(text, "来源选题"),
        "version": f"v{ver}",
        "created_at": _field(text, "创建时间"),
        "slug": _field(text, "slug"),
        "path": str(md.relative_to(md.parents[1])),  # 相对 文案虾/
    }


def _next_version(platform_dir: Path, source_topic: str, slug: str) -> int:
    if not platform_dir.exists():
        return 1
    n = 0
    for md in platform_dir.glob("*.md"):
        t = _field(md.read_text(encoding="utf-8"), "来源选题")
        s = _field(md.read_text(encoding="utf-8"), "slug")
        if t == source_topic or s == slug:
            n += 1
    return n + 1


def _save_index(base: Path) -> int:
    rows = []
    for plat_dir in sorted(base.iterdir()):
        if plat_dir.is_dir():
            for md in sorted(plat_dir.glob("*.md")):
                rows.append(_parse_article(md))
    lines = [
        "# 文案虾 内容索引",
        "",
        "| 日期 | 标题 | 平台 | 来源选题 | 版本 | 路径 |",
        "|------|------|------|----------|------|------|",
    ]
    for r in rows:
        date = (r["created_at"][:10] if r["created_at"] else "")
        lines.append(
            f"| {date} | {r['title']} | {r['platform']} | "
            f"{r['source_topic']} | {r['version']} | {r['path']} |"
        )
    (base.parent / "索引.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(rows)


def archive(article: dict, base: Path) -> Path:
    _validate(article)
    now = dt.datetime.now()
    slug = article.get("slug") or _slugify(article["title"])
    article["slug"] = slug
    article["created_at"] = article.get("created_at") or _now_iso()
    plat_dir = base / article["platform"]
    plat_dir.mkdir(parents=True, exist_ok=True)
    version = _next_version(plat_dir, article.get("source_topic", ""), slug)
    fname = f"{now.strftime('%Y-%m-%d')}-{slug}.md"
    if (plat_dir / fname).exists():
        fname = f"{now.strftime('%Y-%m-%d')}-{slug}-v{version}.md"
    out = plat_dir / fname
    out.write_text(_to_markdown(article, version), encoding="utf-8")
    total = _save_index(base)
    return out


def list_articles(base: Path, platform: str = None) -> list:
    if not base.exists():
        return []
    rows = []
    for plat_dir in sorted(base.iterdir()):
        if not plat_dir.is_dir():
            continue
        if platform and plat_dir.name != platform:
            continue
        for md in sorted(plat_dir.glob("*.md")):
            rows.append(_parse_article(md))
    return rows


def main():
    ap = argparse.ArgumentParser(description="文案虾成品归档与索引")
    ap.add_argument("--base", default=str(DEFAULT_BASE), help="成品根目录")
    ap.add_argument("--archive", action="store_true", help="归档一篇成文(从 --json 或 stdin)")
    ap.add_argument("--json", help="成文 JSON 文件路径")
    ap.add_argument("--list", action="store_true", help="列出已归档成文")
    ap.add_argument("--platform", help="按平台过滤(list)")
    ap.add_argument("--index", action="store_true", help="重建 索引.md")
    args = ap.parse_args()
    base = Path(args.base)

    if args.archive:
        raw = Path(args.json).read_text(encoding="utf-8") if args.json else sys.stdin.read()
        article = json.loads(raw)
        path = archive(article, base)
        print(f"ARCHIVED {path}")
        return

    if args.list:
        rows = list_articles(base, platform=args.platform)
        if not rows:
            print("NO_ARTICLES")
            return
        for r in rows:
            print(f"{r['version']:<4} | {r['platform']:<6} | {r['title']}")
        print(f"\nTOTAL {len(rows)}")
        return

    if args.index:
        total = _save_index(base)
        print(f"INDEX_REBUILT {total} entries")
        return

    ap.print_help()


if __name__ == "__main__":
    main()
