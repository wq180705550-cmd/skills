#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
审核虾 — 文章质量审核脚本 (audit_article.py)

对「文案虾」输出的 Markdown 文章做 6 维度质量审核：
  1. 主标题吸引力 (硬)
  2. 小标题简洁性 (硬) — 必须用 ## 标记
  3. 数据准确性   (硬)
  4. 事实一致性   (软, 推导) — 可选选题卡对齐
  5. AI味检测     (软, 推导) — 衔接文案虾 humanize-guide
  6. 平台适配性   (软, 推导)

仅依赖标准库。输出每维度评分 + 发布闸门结论，并写 <原名>.audit.md 报告。

用法:
  python audit_article.py <文章.md | 目录>
      [--platform 小红书|公众号|知乎|今日头条]
      [--topic-card 选题卡.md]
      [--threshold 70]
      [--report-dir DIR]
      [--json]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

CURRENT_YEAR = 2026

PLATFORM_BANDS = {
    "小红书": (800, 1500),
    "公众号": (1500, 3000),
    "知乎": (2000, 5000),
    "今日头条": (600, 1200),
    "头条": (600, 1200),
}

# 文案虾 humanize-guide 反模式 (AI味) — 详见 references/humanize-guide.md
AI_TRACE_PHRASES = [
    "首先", "其次", "最后", "综上所述", "值得注意的是", "在当今社会",
    "近年来", "众所周知", "不难看出", "总而言之", "此外", "与此同时",
    "不可否认", "显而易见", "随着社会的不断发展", "在这个充满挑战的时代",
]

HOOK_WORDS = ["为什么", "如何", "怎样", "揭秘", "背后", "真相", "其实", "竟然",
              "居然", "原来", "别再", "千万", "慎用", "？", "?"]
CLICKBAIT_WORDS = ["最", "第一", "必看", "惊呆", "震惊", "干货", "速看", "收藏"]

HARD = ["主标题吸引力", "小标题简洁性", "数据准确性"]
SOFT = ["事实一致性", "AI味检测", "平台适配性"]


def _strip_code(text: str) -> str:
    """移除代码块，避免误判标题/数字。"""
    return re.sub(r"```.*?```", "", text, flags=re.S)


def parse_structure(text: str):
    clean = _strip_code(text)
    headings = []  # (level, title)
    for m in re.finditer(r"^(#{1,6})\s+(.+?)\s*#*\s*$", clean, re.M):
        headings.append((len(m.group(1)), m.group(2).strip()))
    main_title = headings[0][1] if headings and headings[0][0] == 1 else ""
    subheadings = [t for lv, t in headings if lv == 2]
    deep_headings = [t for lv, t in headings if lv >= 3]
    pseudo = []
    for line in clean.splitlines():
        s = line.strip()
        if 2 <= len(s) <= 20 and s.startswith("**") and s.endswith("**") and not s.startswith("##"):
            pseudo.append(s.strip("*"))
    return {
        "main_title": main_title,
        "subheadings": subheadings,
        "deep_headings": deep_headings,
        "pseudo_subheadings": pseudo,
        "heading_count": len(headings),
    }


def audit_title(struct, text):
    title = struct["main_title"]
    findings = []
    if not title:
        return 0, ["未检测到主标题(# 一级标题)"]
    score = 60
    tl = len(title)
    if 8 <= tl <= 26:
        score += 15
    elif tl < 6:
        score -= 15
        findings.append("主标题过短(<6字)，信息量不足")
    elif tl > 30:
        score -= 15
        findings.append("主标题过长(>30字)，不易记忆")
    if any(w in title for w in HOOK_WORDS):
        score += 15
        findings.append("含悬念/反问元素，吸引力+")
    if any(w in title for w in CLICKBAIT_WORDS):
        score += 5
        findings.append("含强吸引词，确保正文内容匹配避免标题党")
    title_tokens = [w for w in re.findall(r"[\u4e00-\u9fff]{2,}", title)]
    if title_tokens:
        hits = sum(1 for t in title_tokens if t in text)
        if hits / len(title_tokens) < 0.5:
            score -= 20
            findings.append("标题关键词与正文重合度低，可能偏题/标题党")
    score = max(0, min(100, score))
    return score, findings


def audit_subheadings(struct):
    findings = []
    score = 100
    if not struct["subheadings"]:
        score -= 45
        findings.append("缺少 ## 小标题，结构不完整")
    for h in struct["deep_headings"]:
        score -= 10
        findings.append(f"深层级标题「{h}」建议改为 ## 标记")
    for p in struct["pseudo_subheadings"]:
        score -= 8
        findings.append(f"疑似小标题未用##标记(加粗伪标题):「{p}」")
    for h in struct["subheadings"]:
        if len(h) > 18:
            score -= 5
            findings.append(f"小标题偏长(>{len(h)}字):「{h}」")
    score = max(0, min(100, score))
    if not findings:
        findings.append("小标题均用 ## 标记，简洁且层次清晰")
    return score, findings


def _extract_numbers(text):
    clean = _strip_code(text)
    nums = re.findall(r"\d{1,3}(?:,\d{3})*(?:\.\d+)?%?|\d+\.\d+|\d+", clean)
    years = re.findall(r"\b(19|20)\d{2}\b", clean)
    return nums, years


def audit_data(text):
    findings = []
    nums, years = _extract_numbers(text)
    score = 100
    suspicious = []
    for y in years:
        if int(y) > CURRENT_YEAR + 1:
            suspicious.append(f"年份 {y} 超过当前({CURRENT_YEAR})，疑似笔误")
    for n in nums:
        if n.endswith("%"):
            try:
                if float(n.rstrip("%")) > 100:
                    suspicious.append(f"百分比 {n} > 100，需确认是否含上下文")
            except ValueError:
                pass
    if re.search(r"(约|大概|大约|近|超)\s*\d", _strip_code(text)):
        suspicious.append("存在模糊限定词紧邻精确数字，需核实")
    if suspicious:
        score -= min(40, 12 * len(suspicious))
        findings.extend(suspicious)
    has_num = len(nums) > 0
    has_cite = bool(re.search(r"【[^】]+】|\[[^\]]+\]|据[说源]|来源|引用|公开数据", text))
    if has_num and not has_cite:
        score -= 20
        findings.append("正文含数字但未见引用标记(【】/据/来源)，引用依据不足")
    if not findings:
        findings.append("数据抽取完成，未发现明显异常；仍建议人工复核关键数字")
    findings.append(f"[需人工核查] 共抽取数字 {len(nums)} 个、年份 {len(years)} 个，请逐条核实")
    score = max(0, min(100, score))
    return score, findings


def audit_consistency(text, topic_card_path=None):
    findings = []
    score = 85
    if topic_card_path:
        p = Path(topic_card_path)
        if p.exists():
            tc = p.read_text(encoding="utf-8")
            points = re.findall(r"-\s*\*(?:核心观点|core_points|要点)\*?\s*[:：]?\s*(.+)", tc)
            if not points:
                points = re.findall(r"核心观点[：:]\s*(.+)", tc)
            if points:
                missing = []
                for pt in points[:8]:
                    kw = re.findall(r"[\u4e00-\u9fff]{2,}", pt)[:3]
                    if kw and not any(k in text for k in kw):
                        missing.append(pt[:20])
                if missing:
                    score -= min(30, 8 * len(missing))
                    findings.append(f"与选题卡对齐缺失 {len(missing)} 条核心观点")
                else:
                    findings.append("核心观点均已体现在正文中")
    clean = _strip_code(text)
    pairs = re.findall(r"([\u4e00-\u9fff]{2,4})[^\n]{0,30}?(\d[\d,\.]*%?)", clean)
    seen = {}
    for ent, val in pairs:
        if ent in seen and seen[ent] != val:
            findings.append(f"同一实体「{ent}」出现不一致数字: {seen[ent]} vs {val}")
            score -= 10
        else:
            seen[ent] = val
    if not findings:
        findings.append("未检测到明显事实矛盾")
    score = max(0, min(100, score))
    return score, findings


def audit_ai_trace(text):
    findings = []
    cnt = 0
    hits = []
    for ph in AI_TRACE_PHRASES:
        c = text.count(ph)
        if c:
            cnt += c
            hits.append(f"{ph}×{c}")
    score = max(0, 100 - cnt * 12)
    if hits:
        findings.append(f"命中AI味短语: {', '.join(hits)} → 建议回炉润色(衔接文案虾步骤③)")
    else:
        findings.append("未检测到典型AI味短语")
    return score, findings


def audit_platform(text, platform):
    findings = []
    score = 100
    chars = len(re.sub(r"\s", "", _strip_code(text)))
    band = PLATFORM_BANDS.get(platform)
    if band:
        lo, hi = band
        if chars < lo:
            score -= 15
            findings.append(f"字数 {chars} 偏少，{platform} 建议 {lo}-{hi} 字")
        elif chars > hi:
            score -= 15
            findings.append(f"字数 {chars} 偏多，{platform} 建议 {lo}-{hi} 字")
        else:
            findings.append(f"字数 {chars} 落在 {platform} 推荐区间")
    if platform == "小红书":
        if not re.search(r"[\U0001F300-\U0001FAFF\u2600-\u27BF]", text):
            score -= 15
            findings.append("小红书建议加入 emoji 增强观感")
        if "#" not in text:
            score -= 10
            findings.append("小红书建议添加 #话题标签 便于分发")
    if not band and platform:
        findings.append(f"未配置 {platform} 字数区间，仅做通用检查")
    score = max(0, min(100, score))
    return score, findings


def audit_file(path: Path, platform=None, topic_card=None, threshold=70):
    text = path.read_text(encoding="utf-8")
    struct = parse_structure(text)
    s1, f1 = audit_title(struct, text)
    s2, f2 = audit_subheadings(struct)
    s3, f3 = audit_data(text)
    s4, f4 = audit_consistency(text, topic_card)
    s5, f5 = audit_ai_trace(text)
    s6, f6 = audit_platform(text, platform)
    results = {
        "主标题吸引力": (s1, f1, "hard"),
        "小标题简洁性": (s2, f2, "hard"),
        "数据准确性": (s3, f3, "hard"),
        "事实一致性": (s4, f4, "soft"),
        "AI味检测": (s5, f5, "soft"),
        "平台适配性": (s6, f6, "soft"),
    }
    soft_th = max(40, threshold - 30)
    hard_pass = all(results[d][0] >= threshold for d in HARD)
    soft_pass = all(results[d][0] >= soft_th for d in SOFT)
    verdict = ("✅ 建议发布" if hard_pass and soft_pass else
               "⚠️ 需修订（硬指标未达标）" if not hard_pass else
               "⚠️ 建议润色（软指标偏弱）")
    return {
        "file": str(path),
        "platform": platform,
        "threshold": threshold,
        "soft_threshold": soft_th,
        "results": results,
        "hard_pass": hard_pass,
        "soft_pass": soft_pass,
        "publish": hard_pass and soft_pass,
        "verdict": verdict,
    }


def render_report(rep: dict) -> str:
    lines = [
        f"# 审核报告 — {Path(rep['file']).name}",
        "",
        f"- 平台: {rep['platform'] or '未指定'}  | 阈值: 硬 {rep['threshold']} / 软 {rep['soft_threshold']}",
        f"- 结论: **{rep['verdict']}**",
        "",
        "| 维度 | 类型 | 评分 | 结论 |",
        "|------|------|------|------|",
    ]
    for name, (sc, f, kind) in rep["results"].items():
        ok = (kind == "hard" and sc >= rep["threshold"]) or (kind == "soft" and sc >= rep["soft_threshold"])
        lines.append(f"| {name} | {kind} | {sc} | {'✅' if ok else '⚠️'} |")
    lines.append("")
    for name, (sc, f, kind) in rep["results"].items():
        lines.append(f"## {name}（{sc}分）")
        for item in f:
            lines.append(f"- {item}")
        lines.append("")
    lines.append(f"> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}  |  审核虾 shenhe-xia")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description="审核虾 — 文章质量审核")
    ap.add_argument("path", help="文章 .md 或目录")
    ap.add_argument("--platform", default=None, help="目标平台: 小红书/公众号/知乎/今日头条")
    ap.add_argument("--topic-card", default=None, help="选题卡 .md（用于事实一致性对齐）")
    ap.add_argument("--threshold", type=int, default=70, help="硬指标发布阈值(默认70)")
    ap.add_argument("--report-dir", default=None, help="审计报告输出目录(默认与原文同目录)")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    args = ap.parse_args(argv)

    base = Path(args.path)
    if base.is_dir():
        files = [p for p in sorted(base.glob("*.md"))
                 if p.name != "索引.md" and not p.name.endswith(".audit.md")]
    else:
        files = [base]

    reports = []
    for f in files:
        rep = audit_file(f, platform=args.platform, topic_card=args.topic_card, threshold=args.threshold)
        reports.append(rep)
        if args.json:
            print(json.dumps(rep, ensure_ascii=False, indent=2))
        else:
            print(render_report(rep))
            print("=" * 60)
        rdir = Path(args.report_dir) if args.report_dir else f.parent
        rdir.mkdir(parents=True, exist_ok=True)
        (rdir / (f.stem + ".audit.md")).write_text(render_report(rep), encoding="utf-8")

    if len(reports) > 1:
        pub = sum(1 for r in reports if r["publish"])
        print(f"\n汇总: {len(reports)} 篇，{pub} 篇建议发布，{len(reports) - pub} 篇需修订/润色")
    return 0


if __name__ == "__main__":
    sys.exit(main())
