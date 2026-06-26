#!/usr/bin/env python3
"""
Stop Hook 调度脚本
在会话结束时执行，用于清理和上报
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
    
    hooks = config.get("hooks", {}).get("Stop", [])
    
    for hook in hooks:
        matcher = hook.get("matcher", "")
        command = hook.get("command", "")
        timeout = hook.get("timeout", 5000) / 1000
        
        # Stop 事件默认匹配所有（matcher 通常为 "*"）
        if not match(matcher, "*"):
            continue
        
        # 执行 hook 脚本
        try:
            result = subprocess.run(
                command,
                input=json.dumps(event_data),
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.stdout:
                print(result.stdout)
        except Exception as e:
            print(f"[STOP HOOK ERROR] {e}", file=sys.stderr)
    
    sys.exit(0)


def match(matcher, tool):
    """匹配工具名"""
    if matcher == "*":
        return True
    if matcher == tool:
        return True
    return False


if __name__ == "__main__":
    main()
