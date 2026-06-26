#!/usr/bin/env python3
"""
PreToolUse Hook 调度脚本
在工具调用前执行，可阻断或修改
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
        # 无配置，默认放行
        print(json.dumps({"decision": "allow"}))
        sys.exit(0)
    
    with open(HOOKS_YAML, "r") as f:
        config = yaml.safe_load(f)
    
    hooks = config.get("hooks", {}).get("PreToolUse", [])
    
    for hook in hooks:
        matcher = hook.get("matcher", "")
        command = hook.get("command", "")
        timeout = hook.get("timeout", 3000) / 1000
        
        # 匹配工具名
        tool = event_data.get("tool", "")
        if not match(matcher, tool):
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
                decision = json.loads(result.stdout)
                
                # 阻断
                if decision.get("decision") == "block":
                    print(json.dumps(decision))
                    sys.exit(0)
                
                # 修改参数（暂不支持）
                elif decision.get("decision") == "modify":
                    event_data["params"] = decision.get("params", event_data["params"])
            
        except subprocess.TimeoutExpired:
            # 超时，使用 on_error 配置
            on_error = hook.get("on_error", "allow")
            if on_error == "block":
                print(json.dumps({
                    "decision": "block",
                    "reason": "Hook 执行超时"
                }))
                sys.exit(0)
        
        except Exception as e:
            print(f"[HOOK ERROR] {e}", file=sys.stderr)
    
    # 所有 hooks 通过，放行
    print(json.dumps({"decision": "allow"}))
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
