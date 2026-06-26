#!/usr/bin/env python3
"""
Stop Hook 示例 — 会话结束清理临时文件 + 生成会话报告
"""

import sys
import json
import time
import os
import glob
from datetime import datetime

def main():
    # 读取事件 JSON
    event = json.load(sys.stdin)
    session_id = event.get("session_id", "unknown")
    duration_sec = event.get("duration_sec", 0)
    task_count = event.get("task_count", 0)

    print(f"[STOP] 会话 {session_id} 结束，开始清理...")

    # 1. 清理临时文件
    temp_patterns = [
        "**/*.tmp",
        "**/*.log",
        "**/__pycache__",
        "**/*.pyc",
        "**/.DS_Store",
        "**/node_modules/.cache"
    ]

    cleaned = 0
    for pattern in temp_patterns:
        for file in glob.glob(pattern, recursive=True):
            try:
                if os.path.isfile(file):
                    os.remove(file)
                    cleaned += 1
                elif os.path.isdir(file):
                    import shutil
                    shutil.rmtree(file)
                    cleaned += 1
            except Exception as e:
                pass

    print(f"[STOP] 清理了 {cleaned} 个临时文件")

    # 2. 生成会话报告
    report = {
        "session_id": session_id,
        "end_time": datetime.now().isoformat(),
        "duration_sec": duration_sec,
        "task_count": task_count,
        "cleaned_files": cleaned
    }

    report_dir = ".claude-hooks/logs"
    os.makedirs(report_dir, exist_ok=True)

    report_file = f"{report_dir}/session_{session_id}.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"[STOP] 会话报告已保存：{report_file}")

    sys.exit(0)

if __name__ == "__main__":
    main()
