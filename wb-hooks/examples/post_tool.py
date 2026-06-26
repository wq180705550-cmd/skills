#!/usr/bin/env python3
"""
PostToolUse Hook 调度脚本
在工具调用后执行，只读记录
"""

import sys
import json
import subprocess
import yaml
from pathlib import Path

HOOKS_YAML = Path(".claude-hooks/hooks.yaml")


def main():
    # 从 stdin 读取事件数据
    event_data = json.load(sys.stdin)
    
    if not HOOKS_YAML.exists():
        sys.exit(0)
    
    with open(HOOKS_YAML, "r") as f:
        config = yaml.safe_load(f)
    
    hooks = config.get("hooks", {}).get("PostToolUse", [])
    
    for hook in hooks:
        matcher = hook.get("matcher", "")
        command = hook.get("command", "")
        timeout = hook.get("timeout", 1000) / 1000
        
        # 匹配工具名
        tool = event_data.get("tool", "")
        if not match(matcher, tool):
            continue
        
        # 异步执行 hook 脚本（不阻塞）
        try:
            subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            ).communicate(input=json.dumps(event_data), timeout=timeout)
        except:
            pass  # PostToolUse hook 失败不阻断
    
    sys.exit(0)


def match(matcher, tool):
    """匹配工具名"""
    if matcher == "*":
        return True
    if matcher == tool:
        return True
    if tool in matcher.split("|"):
        return True
    return False


if __name__ == "__main__":
    main()
