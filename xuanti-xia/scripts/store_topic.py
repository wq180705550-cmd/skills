#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
选题虾 — 选题库存储脚本 (deterministic)

将选题卡持久化到「文案虾/选题库/<分类>/<日期>-<slug>.md」，
并支持列出 / 检索候选池，供选题推荐逻辑消费。

仅依赖标准库。base 路径可配置，默认 ./文案虾/选题库/。

用法:
  # 从 JSON 文件存一个选题
  python store_topic.py --store --json topic.json

  # 从 stdin 读 JSON 存一个选题
  echo '{"title":"...","source":"主题挖掘",...}' | python store_topic.py --store

  # 列出全部选题 (默认仅候选)
  python store_topic.py --list

  # 按状态 / 分类过滤
  python store_topic.py --list --status 候选 --category 财经

  # 改状态
  python store_topic.py --update-status <slug> 已采纳

  # 取单个选题原文
  python store_topic.py --get <slug>
"""

import argparse
import datetime as dt
import json
import re
import sys
import uuid
from pathlib import Path

DEFAULT_BASE = Path.cwd() / "文案虾" / "选题库"
VALID_SOURCES = {"口水稿整理", "主题挖掘", "热点分析"}
VALID_STATUS = {"候选", "已采纳", "已写"}


def _slugify(text: str) -> str:
    """生成文件名安全的短码：去非字母数字，截断。"""
    cleaned = re.sub(r"[^\w一-鿿]+", "-", text.strip()).strip("-")
    cleaned = cleaned.strip("-")
    return (cleaned[:40] or "topic").lower()


def _now_iso() -> str:
    return dt.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def _load_topic(json_input) -> dict:
    if isinstance(json_input, (str, bytes)):
        return json.loads(json_input)
    return json_input


def _validate(topic: dict) -> None:
    if "title" not in topic or not str(topic["title"]).strip():
        raise ValueError("选题卡缺少必填字段 title")
    src = topic.get("source", "主题挖掘")
    if src not in VALID_SOURCES:
        raise ValueError(f"source 必须是 {VALID_SOURCES} 之一，收到: {src}")
    st = topic.get("status", "候选")
    if st not in VALID_STATUS:
        raise ValueError(f"status 必须是 {VALID_STATUS} 之一，收到: {st}")


def _to_markdown(topic: dict) -> str:
    """把选题卡渲染为可读 Markdown 文件。"""
    title = topic["title"]
    lines = [
        f"# {title}",
        "",
        f"- **id**: {topic.get('id', '')}",
        f"- **slug**: {topic.get('slug', '')}",
        f"- **来源**: {topic.get('source', '主题挖掘')}",
        f"- **主主题**: {topic.get('main_topic', title)}",
        f"- **目标受众**: {topic.get('audience', '')}",
        f"- **内容调性**: {topic.get('tone', '')}",
        f"- **EMOS命中**: {', '.join(topic.get('emos_hit', [])) or '—'}",
        f"- **热点关联**: {topic.get('hotspot_link', '—')}",
        f"- **状态**: {topic.get('status', '候选')}",
        f"- **创建时间**: {topic.get('created_at', _now_iso())}",
        "",
        "## 核心观点",
    ]
    for p in topic.get("core_points", []):
        lines.append(f"- {p}")
    if topic.get("reason"):
        lines += ["", "## 推荐理由", "", topic["reason"]]
    lines.append("")
    return "\n".join(lines)


def store(topic: dict, base: Path) -> Path:
    _validate(topic)
    now = dt.datetime.now()
    slug = topic.get("slug") or _slugify(topic["title"])
    topic["id"] = topic.get("id") or uuid.uuid4().hex[:8]
    topic["slug"] = slug
    topic["created_at"] = topic.get("created_at") or _now_iso()
    category = topic.get("category") or "未分类"
    out_dir = base / category
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{now.strftime('%Y-%m-%d')}-{slug}.md"
    # 避免同日同名覆盖：追加短码
    if out_file.exists():
        out_file = out_dir / f"{now.strftime('%Y-%m-%d')}-{slug}-{topic['id']}.md"
    out_file.write_text(_to_markdown(topic), encoding="utf-8")
    return out_file


def _iter_topics(base: Path):
    if not base.exists():
        return
    for md in sorted(base.rglob("*.md")):
        text = md.read_text(encoding="utf-8")
        yield md, text


def _parse_front(text: str) -> dict:
    """从 Markdown 解析关键字段（轻量，不依赖 yaml）。"""
    def field(name):
        m = re.search(rf"-\s*\*\*{name}\*\*\s*:\s*(.+)", text)
        return m.group(1).strip() if m else ""
    return {
        "title": (text.split("\n", 1)[0].lstrip("# ").strip() if text.startswith("# ") else ""),
        "source": field("来源"),
        "status": field("状态"),
        "slug": field("slug"),
    }


def list_topics(base: Path, status=None, category=None) -> list:
    out = []
    for md, text in _iter_topics(base):
        meta = _parse_front(text)
        meta["path"] = str(md)
        # category 由目录名决定
        meta["category"] = md.parent.name
        if status and meta.get("status") != status:
            continue
        if category and meta.get("category") != category:
            continue
        out.append(meta)
    return out


def get_topic(base: Path, slug: str) -> str:
    for md, text in _iter_topics(base):
        if slug in md.name or slug in text:
            return text
    return ""


def update_status(base: Path, slug: str, new_status: str) -> bool:
    if new_status not in VALID_STATUS:
        raise ValueError(f"status 必须是 {VALID_STATUS} 之一")
    for md, text in _iter_topics(base):
        if slug in md.name:
            new_text = re.sub(r"-\s*\*\*状态\*\*\s*:\s*.+",
                              f"- **状态**: {new_status}", text)
            md.write_text(new_text, encoding="utf-8")
            return True
    return False


def main():
    ap = argparse.ArgumentParser(description="选题虾选题库存储工具")
    ap.add_argument("--base", default=str(DEFAULT_BASE), help="选题库根目录")
    ap.add_argument("--store", action="store_true", help="存一个选题(从 --json 或 stdin)")
    ap.add_argument("--json", help="选题 JSON 文件路径")
    ap.add_argument("--list", action="store_true", help="列出选题")
    ap.add_argument("--status", help="过滤状态: 候选/已采纳/已写")
    ap.add_argument("--category", help="过滤分类")
    ap.add_argument("--get", help="取单个选题(slug)")
    ap.add_argument("--update-status", nargs=2, metavar=("SLUG", "STATUS"),
                    help="更新某选题状态")
    args = ap.parse_args()

    base = Path(args.base)

    if args.store:
        raw = Path(args.json).read_text(encoding="utf-8") if args.json else sys.stdin.read()
        topic = _load_topic(raw)
        path = store(topic, base)
        print(f"STORED {path}")
        return

    if args.list:
        rows = list_topics(base, status=args.status, category=args.category)
        if not rows:
            print("NO_TOPICS")
            return
        for r in rows:
            print(f"{r.get('status','?'):<4} | {r.get('category','?'):<8} | {r.get('title','?')}")
        print(f"\nTOTAL {len(rows)}")
        return

    if args.get:
        txt = get_topic(base, args.get)
        print(txt or "NOT_FOUND")
        return

    if args.update_status:
        slug, st = args.update_status
        ok = update_status(base, slug, st)
        print("UPDATED" if ok else "NOT_FOUND")
        return

    ap.print_help()


if __name__ == "__main__":
    main()
