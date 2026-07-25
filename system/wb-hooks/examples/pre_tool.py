#!/usr/bin/env python3
"""
PreToolUse Hook 示例 — 禁止写入 node_modules / 敏感文件
"""

import sys
import json
import os

def main():
    # 读取事件 JSON
    event = json.load(sys.stdin)
    tool = event.get("tool")
    params = event.get("params", {})

    # 检查 Write/Edit 工具
    if tool in ["Write", "Edit"]:
        file_path = params.get("file_path", "")

        # 1. 禁止写入 node_modules
        if "node_modules" in file_path:
            print(json.dumps({
                "decision": "block",
                "reason": f"❌ 禁止写入 node_modules：{file_path}"
            }))
            sys.exit(0)

        # 2. 禁止修改敏感文件
        sensitive_patterns = [
            ".env", ".env.local", ".env.production",
            "id_rsa", "id_ed25519", ".ssh/config",
            "credentials.json", "client_secret.json"
        ]
        if any(p in file_path for p in sensitive_patterns):
            print(json.dumps({
                "decision": "block",
                "reason": f"❌ 禁止修改敏感文件：{file_path}"
            }))
            sys.exit(0)

        # 3. 检查文件大小（防止意外写入大文件）
        content = params.get("content", "")
        if len(content) > 10 * 1024 * 1024:  # 10MB
            print(json.dumps({
                "decision": "block",
                "reason": f"❌ 文件过大（{len(content)} bytes），禁止写入"
            }))
            sys.exit(0)

    # 放行
    print(json.dumps({"decision": "allow"}))
    sys.exit(0)

if __name__ == "__main__":
    main()
