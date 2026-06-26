#!/usr/bin/env python3
"""
PostToolUse Hook 示例 — 记录所有 Read 操作到审计日志
"""

import sys
import json
import time
import os
from datetime import datetime

def main():
    # 读取事件 JSON
    event = json.load(sys.stdin)
    tool = event.get("tool")
    params = event.get("params", {})
    result = event.get("result", {})

    # 构造日志条目
    log_entry = {
        "timestamp": time.time(),
        "datetime": datetime.now().isoformat(),
        "event": "PostToolUse",
        "tool": tool,
        "params": params,
        "result": result,
        "session_id": event.get("session_id", "unknown")
    }

    # 写入日志文件
    log_dir = ".claude-hooks/logs"
    os.makedirs(log_dir, exist_ok=True)

    log_file = f"{log_dir}/hook_audit.log"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

    # 输出到 stdout（记录）
    print(f"[LOG] {tool} {params.get('file_path', '')} -> {result.get('status', 'unknown')}")

    sys.exit(0)

if __name__ == "__main__":
    main()
