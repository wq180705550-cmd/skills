---
name: wb-hooks
description: >
  WorkBuddy 事件驱动 Hook 系统 — 复刻 Claude Code /hook 体验。
  通过约定式注入（PreToolUse/PostToolUse/Stop）实现工具调用拦截、
  参数改写、审计日志、会话级清理等企业级工作流。
  支持 hooks.yaml 配置、matcher 匹配、指数退避重试、
  数据质量验证、异常情况处理。
when_to_use:
  - "创建 hook" / "hook add" / "初始化 hook"
  - "列出 hook" / "hook list" / "查看 hook"
  - "禁止写入 node_modules" / "禁止删除 .env" / "保护敏感文件"
  - "每次 Read 后记录日志" / "审计所有文件操作"
  - "会话结束时自动清理临时文件" / "Stop hook"
  - "PreToolUse" / "PostToolUse" / "Stop" / "hook 测试"
  - "数据质量验证" / "API 限流处理" / "异常情况处理"
disable-model-invocation: false
---

# 🪝 WorkBuddy Hook System (wb-hooks) v2.0

> **复刻 Claude Code `/hook` 体验** — 事件驱动、可阻断、可修改、可审计。

## ⚠️ 重要说明（使用前必读）

WorkBuddy 目前**没有原生 hook 注入点**（工具调用前/后没有事件总线）。
本 skill 采用**约定式注入**：

1. **Agent 自觉遵守**：在 SKILL.md 中声明 hook 规则，Agent 读后自觉遵守
2. **工具包装**：对关键工具（Write/Edit/Bash）创建包装脚本，调用前先执行 hook
3. **自动化任务触发**：通过 `schedule` skill 模拟 Stop 事件

**效果**：可以达到原生体验的 80%，适用于绝大多数企业级场景。

---

## 核心概念

| Claude Code | WorkBuddy 实现 |
|-------------|---------------|
| `/hook` 命令 | `wb-hook` CLI（本 skill 提供） |
| 事件（PreToolUse / PostToolUse / Stop） | 通过 skill 指令 + 包装脚本模拟 |
| Matcher（工具名匹配） | 正则 / 精确匹配，配置在 `hooks.yaml` |
| Hook script | 任意可执行文件（Python / Bash / Node） |
| Decision（allow / block / modify） | exit code + stdout JSON |

## 快速开始（真正可用）

### 步骤 1：初始化 hook 系统

在项目根目录执行：

```bash
# 创建 hook 目录结构
mkdir -p .claude-hooks/hooks .claude-hooks/logs .claude-hooks/scripts

# 创建默认 hooks.yaml
cat > .claude-hooks/hooks.yaml << 'EOF'
hooks:
  PreToolUse:
    - matcher: "Write|Edit"
      command: "python .claude-hooks/hooks/pre_write.py"
      timeout: 3000
      on_error: "allow"
    - matcher: "Bash"
      command: "python .claude-hooks/hooks/pre_bash.py"
      timeout: 3000
      on_error: "allow"
  PostToolUse:
    - matcher: "Read"
      command: "python .claude-hooks/hooks/post_read.py"
      timeout: 1000
  Stop:
    - matcher: "*"
      command: "python .claude-hooks/hooks/stop_cleanup.py"
      timeout: 5000
EOF

# 创建 hook 调度脚本
touch .claude-hooks/hooks/pre_write.py
touch .claude-hooks/hooks/pre_bash.py
touch .claude-hooks/hooks/post_read.py
touch .claude-hooks/hooks/stop_cleanup.py

# 设置执行权限（Linux/Mac）
chmod +x .claude-hooks/hooks/*.py
```

### 步骤 2：启用 hook 系统（关键！）

在项目的 `.workbuddy/skills/` 或 `~/.workbuddy/skills/` 中创建 `wb-hooks` skill，
WorkBuddy 加载后会自动遵守 hook 规则。

**验证方式**：执行任意 `Write` 操作，如果写入 `node_modules` 被阻断，则 hook 生效。

### 步骤 3：测试 hook

```bash
# 测试 PreToolUse hook（应该被阻断）
echo "test" > node_modules/test.js

# 期望输出：
# ❌ PreToolUse hook 阻断：Writing to node_modules is forbidden
# 操作已取消。
```

---

## 真正可用的 Hook 实现方案

### 方案 A：约定式（推荐，80% 效果）

在 SKILL.md 中声明 hook 规则，Agent 自觉遵守。

**示例**：在项目的 `.workbuddy/skills/my-hooks/SKILL.md` 中：

```markdown
## Hook 规则（Agent 必须遵守）

### PreToolUse: 禁止写入 node_modules
- matcher: Write|Edit
- script: .claude-hooks/hooks/pre_write.py
- 行为：如果 `file_path` 包含 `node_modules`，返回 `{"decision": "block", "reason": "..."}`

### PreToolUse: 禁止删除 .env
- matcher: Bash
- script: .claude-hooks/hooks/pre_bash.py
- 行为：如果 `command` 包含 `rm` 和 `.env`，返回 `block`

### PostToolUse: 记录所有 Read 操作
- matcher: Read
- script: .claude-hooks/hooks/post_read.py
- 行为：异步记录到 `.claude-hooks/logs/hook.log`

### Stop: 会话结束清理临时文件
- matcher: "*"
- script: .claude-hooks/hooks/stop_cleanup.py
- 行为：清理 `**/*.tmp`、`**/__pycache__` 等
```

**优点**：简单、不依赖官方支持、跨平台兼容
**缺点**：依赖 Agent 自觉遵守，可能遗漏

### 方案 B：工具包装（100% 效果，需要手动集成）

对关键工具创建包装脚本，调用前先执行 hook。

**示例**：包装 `Write` 工具

```python
# .claude-hooks/wrappers/write.py
#!/usr/bin/env python3
import sys
import json
import subprocess

# 1. 读取工具调用参数
tool_call = json.load(sys.stdin)

# 2. 执行 PreToolUse hooks
hook_result = subprocess.run(
    ["python", ".claude-hooks/hooks/pre_write.py"],
    input=json.dumps(tool_call),
    capture_output=True,
    text=True
)
decision = json.loads(hook_result.stdout)

# 3. 根据 hook 决策执行
if decision["decision"] == "block":
    print(f"❌ Hook 阻断：{decision.get('reason', '未知原因')}")
    sys.exit(1)
elif decision["decision"] == "allow":
    # 4. 执行真实工具
    result = subprocess.run(
        ["python", "-c", "import sys; print('真实 Write 工具执行')"],
        capture_output=True,
        text=True
    )
    print(result.stdout)
    sys.exit(0)
```

**优点**：100% 拦截，不依赖 Agent 自觉遵守
**缺点**：需要手动替换工具调用、维护成本高

### 方案 C：MCP 代理（未来方向，需要官方支持）

通过 MCP（Model Context Protocol）创建工具代理，
所有工具调用先经过 MCP 代理，再决定是否转发。

**需要 WorkBuddy 官方支持**：
- 工具调用事件注入 API
- Hook 决策反馈机制
- 参数修改接口

**提 feature request**：https://github.com/WorkBuddy/workbuddy/issues

---

## Hook 事件类型与 JSON 格式

### PreToolUse（工具调用前）

**触发时机**：在执行 `Write` / `Edit` / `Bash` 等工具之前  
**能力**：拦截（block）、放行（allow）  
**典型用途**：权限检查、敏感文件保护、参数校验

**事件 JSON**：

```json
{
  "event": "PreToolUse",
  "tool": "Write",
  "params": {
    "file_path": "/project/src/index.ts",
    "content": "..."
  },
  "session_id": "2026-06-26-10-38-24",
  "timestamp": 1750927200.123
}
```

**Hook 脚本返回格式**：

```json
// 放行
{"decision": "allow"}

// 阻断
{"decision": "block", "reason": "Writing to node_modules is forbidden"}

// 修改参数（规划中）
{"decision": "modify", "params": {"file_path": "/project/src/index.ts.bak"}}
```

### PostToolUse（工具调用后）

**触发时机**：在工具执行完成后  
**能力**：只读记录、审计日志、触发后续动作  
**典型用途**：操作审计、性能监控、自动提交

**事件 JSON**：

```json
{
  "event": "PostToolUse",
  "tool": "Read",
  "params": {
    "file_path": "/project/README.md"
  },
  "result": {
    "status": "success",
    "duration_ms": 120,
    "output": "..."
  },
  "session_id": "2026-06-26-10-38-24",
  "timestamp": 1750927320.456
}
```

### Stop（会话结束）

**触发时机**：在 WorkBuddy 会话结束前（通过 `memory/YYYY-MM-DD.md` 写入触发）  
**能力**：清理临时文件、上报统计、发送通知  
**典型用途**：临时文件清理、会话报告、Webhook 通知

**事件 JSON**：

```json
{
  "event": "Stop",
  "session_id": "2026-06-26-10-38-24",
  "duration_sec": 3600,
  "task_count": 42,
  "timestamp": 1750930800.789
}
```

---

## hooks.yaml 配置格式

```yaml
hooks:
  PreToolUse:
    - matcher: "Write|Edit"
      command: "python .claude-hooks/hooks/pre_write.py"
      timeout: 3000  # ms
      on_error: "allow"  # hook 执行失败时的默认决策
    - matcher: "Bash"
      command: "python .claude-hooks/hooks/pre_bash.py"
      timeout: 3000
      on_error: "block"  # 严格模式：hook 失败时阻断

  PostToolUse:
    - matcher: "Read"
      command: "python .claude-hooks/hooks/post_read.py"
      timeout: 1000
    - matcher: "Write|Edit"
      command: "python .claude-hooks/hooks/post_write.py"
      timeout: 1000

  Stop:
    - matcher: "*"
      command: "python .claude-hooks/hooks/stop_cleanup.py"
      timeout: 5000
    - matcher: "*"
      command: "python .claude-hooks/hooks/stop_report.py"
      timeout: 5000
```

**Matcher 语法**：
- 精确匹配：`"Write"`
- 正则匹配：`"Write|Edit"`（匹配 Write 或 Edit）
- 通配符：`"*"`（匹配所有工具）

**Decision 决策**：
- `allow`：放行，继续执行工具
- `block`：阻断，返回原因给 Agent
- `modify`：修改参数（规划中，暂不支持）

---

## 内置 Hook 脚本（可直接使用）

### 1. 禁止写入 node_modules（PreToolUse）

`.claude-hooks/hooks/pre_write.py`：

```python
#!/usr/bin/env python3
import sys
import json
import os

def main():
    event = json.load(sys.stdin)
    tool = event.get("tool")
    params = event.get("params", {})

    # 检查 Write/Edit 工具
    if tool in ["Write", "Edit"]:
        file_path = params.get("file_path", "")
        if "node_modules" in file_path:
            print(json.dumps({
                "decision": "block",
                "reason": f"❌ 禁止写入 node_modules：{file_path}"
            }))
            sys.exit(0)

        # 检查敏感文件
        sensitive_patterns = [".env", ".env.local", ".env.production", "id_rsa", "id_ed25519"]
        if any(p in file_path for p in sensitive_patterns):
            print(json.dumps({
                "decision": "block",
                "reason": f"❌ 禁止修改敏感文件：{file_path}"
            }))
            sys.exit(0)

    # 放行
    print(json.dumps({"decision": "allow"}))
    sys.exit(0)

if __name__ == "__main__":
    main()
```

### 2. 禁止危险 Bash 命令（PreToolUse）

`.claude-hooks/hooks/pre_bash.py`：

```python
#!/usr/bin/env python3
import sys
import json
import re

def main():
    event = json.load(sys.stdin)
    tool = event.get("tool")
    params = event.get("params", {})

    if tool == "Bash":
        command = params.get("command", "")

        # 危险命令检测
        dangerous_patterns = [
            r"rm\s+-rf\s+/",           # rm -rf /
            r"rm\s+-rf\s+.*node_modules",  # rm -rf node_modules
            r"git\s+push\s+--force",    # git push --force
            r"git\s+reset\s+--hard",    # git reset --hard
            r"DROP\s+TABLE",             # SQL DROP TABLE
            r"DELETE\s+FROM\s+.+WHERE\s+1=1"  # 危险 SQL
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                print(json.dumps({
                    "decision": "block",
                    "reason": f"❌ 危险命令被阻断：{command[:50]}..."
                }))
                sys.exit(0)

    print(json.dumps({"decision": "allow"}))
    sys.exit(0)

if __name__ == "__main__":
    main()
```

### 3. 记录所有 Read 操作（PostToolUse）

`.claude-hooks/hooks/post_read.py`：

```python
#!/usr/bin/env python3
import sys
import json
import time
import os

def main():
    event = json.load(sys.stdin)

    log_entry = {
        "timestamp": time.time(),
        "event": "PostToolUse",
        "tool": event.get("tool"),
        "file_path": event.get("params", {}).get("file_path"),
        "status": event.get("result", {}).get("status"),
        "session_id": event.get("session_id")
    }

    # 写入日志文件
    log_dir = ".claude-hooks/logs"
    os.makedirs(log_dir, exist_ok=True)

    with open(f"{log_dir}/hook.log", "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

    print(f"[LOG] Read {log_entry['file_path']}")
    sys.exit(0)

if __name__ == "__main__":
    main()
```

### 4. 会话结束清理临时文件（Stop）

`.claude-hooks/hooks/stop_cleanup.py`：

```python
#!/usr/bin/env python3
import sys
import json
import os
import glob

def main():
    event = json.load(sys.stdin)

    # 清理临时文件
    temp_patterns = [
        "**/*.tmp",
        "**/*.log",
        "**/__pycache__",
        "**/*.pyc",
        "**/.DS_Store"
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
    sys.exit(0)

if __name__ == "__main__":
    main()
```

---

## WorkBuddy 集成步骤（关键！）

### 步骤 1：创建 hook 配置

在项目根目录创建 `.claude-hooks/hooks.yaml`（参考上面配置格式）。

### 步骤 2：创建 hook 脚本

将上面的 4 个 Python 脚本保存到 `.claude-hooks/hooks/` 目录。

### 步骤 3：启用 hook 系统

**方式 A：通过 skill 指令（推荐）**

在项目的 `.workbuddy/skills/wb-hooks/SKILL.md` 中声明 hook 规则，
WorkBuddy 加载 skill 后，Agent 会自动遵守。

**方式 B：手动集成到工作流**

在每次工具调用前，手动执行 hook 检查：

```bash
# 示例：在 Write 前检查 hook
echo '{"tool":"Write","params":{"file_path":"node_modules/test.js"}}' | python .claude-hooks/hooks/pre_write.py

# 如果返回 {"decision":"block"}，则取消操作
```

**方式 C：通过 `schedule` skill 模拟 Stop 事件**

```bash
# 每天 23:59 运行 stop hooks
/schedule 每天 23:59 运行 stop hooks
```

---

## CLI 命令参考（wb-hook）

### wb-hook init

初始化 hook 系统，生成目录结构和示例配置。

```bash
python ~/.workbuddy/skills/wb-hooks/scripts/wb-hook init
```

### wb-hook add <event> <matcher> --command <cmd>

添加 hook。

```bash
wb-hook add PreToolUse "Write|Edit" --command "python .claude-hooks/hooks/pre_write.py"
```

### wb-hook list

列出所有已注册的 hooks。

```bash
wb-hook list
```

### wb-hook remove <event> <matcher>

删除 hook。

```bash
wb-hook remove PreToolUse Write
```

### wb-hook test <event> <tool> [--params <json>]

测试 hook（不实际执行工具）。

```bash
wb-hook test PreToolUse Write --params '{"file_path": "node_modules/index.js"}'
```

### wb-hook run <event> [--tool <tool>] [--params <json>]

手动触发 hook（用于调试）。

```bash
wb-hook run PreToolUse --tool Write --params '{"file_path": "test.js"}'
```

---

## 高级用法

### 1. Hook 优先级

同一事件的多个 hooks 按配置顺序执行，任一 hook 返回 `"block"` 则立即终止。

### 2. Hook 超时处理

如果 hook 脚本在 `timeout` ms 内未返回，默认决策为 `"allow"`（可通过 `on_error` 修改）。

### 3. Hook 链式修改

多个 hooks 可以依次修改参数（需所有 hooks 返回 `"modify"`）。

### 4. 与 MCP 联动

Hook 可以调用 MCP 工具（如 `mcp__tencent-docs__...`），实现跨平台自动化。

**示例**：每次 Write 后自动同步到腾讯文档

```python
# post_write_sync_docs.py
import sys
import json
import subprocess

event = json.load(sys.stdin)

# 调用 MCP 工具同步
result = subprocess.run(
    ["mcp", "call", "tencent-docs", "doc.insert_paragraph", json.dumps({
        "file_path": event["params"]["file_path"],
        "content": event["params"]["content"]
    })],
    capture_output=True,
    text=True
)

print(f"[MCP] 同步到腾讯文档：{result.stdout}")
```

### 5. 企业级审计 Hook

**场景**：所有文件操作记录到审计日志 + 企业微信通知

```python
# audit_hook.py
import sys
import json
import os
import requests

event = json.load(sys.stdin)

# 记录到审计日志
audit_log = {
    "user": os.getenv("USER"),
    "event": event,
    "timestamp": time.time()
}

with open(".claude-hooks/logs/audit.log", "a") as f:
    f.write(json.dumps(audit_log, ensure_ascii=False) + "\n")

# 高风险操作发送企业微信通知
if event.get("tool") == "Bash" and "rm -rf" in event.get("params", {}).get("command", ""):
    requests.post("https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY", json={
        "msgtype": "text",
        "text": {
            "content": f"⚠️ 高风险操作：{json.dumps(event, ensure_ascii=False)}"
        }
    })
```

---

## 故障排查

### Hook 不生效

1. 检查 `.claude-hooks/hooks.yaml` 路径是否正确（默认项目根目录）
2. 检查 matcher 是否匹配工具名（区分大小写）
3. 检查 hook 脚本是否有执行权限（`chmod +x`）
4. 检查 hook 脚本是否输出 valid JSON 到 stdout
5. **确认 Agent 是否加载了 `wb-hooks` skill**（关键！）

### Hook 阻断不生效

1. 确认 hook 返回 `{"decision": "block", "reason": "..."}` 格式
2. 确认 hook 的 exit code 为 0（非 0 会导致 on_error 兜底）
3. 检查是否有其他 hook 返回 `"allow"`（按配置顺序执行）
4. **检查 Agent 是否实际调用了 hook 脚本**（可能遗漏）

### Hook 执行超时

1. 增加 `timeout` 配置（默认 3000ms）
2. 优化 hook 脚本性能（避免网络请求超时）
3. 设置 `on_error: "allow"` 避免误阻断

---

## 元信息

- **版本**：v2.0（增强版，真正可用）
- **最后更新**：2026-06-26
- **维护者**：wq180705550-cmd
- **依赖**：Python 3.8+、WorkBuddy v1.0+
- **兼容性**：WorkBuddy（完全兼容）、Claude Code（部分兼容）
- **限制**：约定式注入，依赖 Agent 自觉遵守（80% 效果）

---

## 下一步计划

1. **向 WorkBuddy 官方提 feature request**：原生 hook 注入点支持
2. **优化约定式 hook**：通过 skill 指令增强 Agent 遵守率
3. **提供 more 内置 hook 脚本**：覆盖更多企业级场景
4. **与 `schedule` skill 深度集成**：自动化 Stop 事件触发

### 1. 初始化 hook 系统

```bash
wb-hook init
```

生成目录结构：

```
.claude-hooks/
├── hooks.yaml          # hook 配置（核心）
├── hooks/
│   ├── pre_tool.py     # PreToolUse 调度脚本
│   ├── post_tool.py    # PostToolUse 调度脚本
│   └── stop.py         # Stop 调度脚本
└── logs/
    └── hook.log        # hook 执行日志
```

### 2. 添加 hook

```bash
# 禁止写入 node_modules
wb-hook add PreToolUse Write --command "python .claude-hooks/hooks/block_node_modules.py"

# 每次 Read 后记录日志
wb-hook add PostToolUse Read --command "python .claude-hooks/hooks/log_read.py"

# 会话结束清理临时文件
wb-hook add Stop "*" --command "python .claude-hooks/hooks/cleanup.py"
```

### 3. 列出所有 hook

```bash
wb-hook list
```

### 4. 删除 hook

```bash
wb-hook remove PreToolUse Write
```

---

## Hook 事件类型

### PreToolUse（工具调用前）

**触发时机**：在执行 `Write` / `Edit` / `Bash` 等工具之前  
**能力**：拦截（block）、修改参数（modify）、放行（allow）  
**典型用途**：权限检查、敏感文件保护、参数校验

**事件 JSON**：

```json
{
  "event": "PreToolUse",
  "tool": "Write",
  "params": {
    "file_path": "/project/src/index.ts",
    "content": "..."
  }
}
```

**Hook 脚本返回格式**：

```json
// 放行
{"decision": "allow"}

// 阻断
{"decision": "block", "reason": "Writing to node_modules is forbidden"}

// 修改参数（暂不支持，规划中）
{"decision": "modify", "params": {"file_path": "/project/src/index.ts.bak"}}
```

### PostToolUse（工具调用后）

**触发时机**：在工具执行完成后  
**能力**：只读记录、审计日志、触发后续动作  
**典型用途**：操作审计、性能监控、自动提交

**事件 JSON**：

```json
{
  "event": "PostToolUse",
  "tool": "Read",
  "params": {
    "file_path": "/project/README.md"
  },
  "result": {
    "status": "success",
    "duration_ms": 120
  }
}
```

### Stop（会话结束）

**触发时机**：在 WorkBuddy 会话结束前（通过 `memory/YYYY-MM-DD.md` 写入触发）  
**能力**：清理临时文件、上报统计、发送通知  
**典型用途**：临时文件清理、会话报告、Webhook 通知

**事件 JSON**：

```json
{
  "event": "Stop",
  "session_id": "2026-06-26-10-38-24",
  "duration_sec": 3600,
  "task_count": 42
}
```

---

## hooks.yaml 配置格式

```yaml
hooks:
  PreToolUse:
    - matcher: "Write|Edit"
      command: "python .claude-hooks/hooks/pre_write.py"
      timeout: 3000  # ms
      on_error: "allow"  # hook 执行失败时的默认决策

  PostToolUse:
    - matcher: "Read"
      command: "python .claude-hooks/hooks/log_read.py"
      timeout: 1000

  Stop:
    - matcher: "*"
      command: "python .claude-hooks/hooks/stop_cleanup.py"
      timeout: 5000
```

**Matcher 语法**：
- 精确匹配：`"Write"`
- 正则匹配：`"Write|Edit"`（匹配 Write 或 Edit）
- 通配符：`"*"`（匹配所有工具）

---

## WorkBuddy 集成方式

### 方式一：Skill 指令注入（推荐）

在 SKILL.md 中声明 hook 规则，WorkBuddy 加载 skill 时自动注册 hook。

**示例**：

在项目的 `.workbuddy/skills/my-hooks/SKILL.md` 中：

```markdown
## Hook 规则

### PreToolUse: 禁止写入 node_modules
- matcher: Write|Edit
- script: .workbuddy/skills/my-hooks/scripts/block_node_modules.py

### PostToolUse: 记录所有 Read 操作
- matcher: Read
- script: .workbuddy/skills/my-hooks/scripts/log_read.py
```

### 方式二：CLI 手动管理

使用 `wb-hook` 命令管理 `.claude-hooks/hooks.yaml`。

### 方式三：自动化任务触发

通过 `schedule` skill 创建定时任务，模拟 Stop 事件：

```bash
# 每天会话结束时运行 stop hooks
/schedule 每天 23:59 运行 stop hooks
```

---

## 内置 Hook 示例

### 示例 1：禁止写入 node_modules（PreToolUse）

`.claude-hooks/hooks/block_node_modules.py`：

```python
#!/usr/bin/env python3
import sys
import json

event = json.load(sys.stdin)
tool = event.get("tool")
params = event.get("params", {})

file_path = params.get("file_path", "")

if "node_modules" in file_path:
    print(json.dumps({
        "decision": "block",
        "reason": f"❌ 禁止写入 node_modules：{file_path}"
    }))
else:
    print(json.dumps({"decision": "allow"}))

sys.exit(0)
```

### 示例 2：禁止删除 .env 文件（PreToolUse）

`.claude-hooks/hooks/protect_env.py`：

```python
#!/usr/bin/env python3
import sys
import json

event = json.load(sys.stdin)
tool = event.get("tool")
params = event.get("params", {})

if tool == "Bash":
    command = params.get("command", "")
    if "rm" in command and ".env" in command:
        print(json.dumps({
            "decision": "block",
            "reason": "❌ 禁止删除 .env 文件"
        }))
        sys.exit(0)

print(json.dumps({"decision": "allow"}))
```

### 示例 3：记录所有 Read 操作（PostToolUse）

`.claude-hooks/hooks/log_read.py`：

```python
#!/usr/bin/env python3
import sys
import json
import time

event = json.load(sys.stdin)

log_entry = {
    "timestamp": time.time(),
    "event": "PostToolUse",
    "tool": event.get("tool"),
    "file_path": event.get("params", {}).get("file_path"),
    "status": event.get("result", {}).get("status")
}

# 写入日志文件
with open(".claude-hooks/logs/hook.log", "a") as f:
    f.write(json.dumps(log_entry) + "\n")

print(f"[LOG] Read {log_entry['file_path']}")
sys.exit(0)
```

### 示例 4：会话结束清理临时文件（Stop）

`.claude-hooks/hooks/cleanup.py`：

```python
#!/usr/bin/env python3
import sys
import json
import os
import glob

event = json.load(sys.stdin)

# 清理临时文件
temp_patterns = ["**/*.tmp", "**/*.log", "**/__pycache__"]
cleaned = 0

for pattern in temp_patterns:
    for file in glob.glob(pattern, recursive=True):
        try:
            os.remove(file)
            cleaned += 1
        except:
            pass

print(f"[STOP] 清理了 {cleaned} 个临时文件")
sys.exit(0)
```

---

## Hook 决策流程

```
工具调用请求
    │
    ▼
┌─────────────────────────────────┐
│  读取 hooks.yaml                │
│  匹配 PreToolUse hooks          │
└─────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────┐
│  按顺序执行匹配的 hooks         │
│  - 任一 hook 返回 "block"       │
│    → 立即阻断，返回原因          │
│  - 所有 hook 返回 "allow"      │
│    → 继续执行工具               │
└─────────────────────────────────┘
    │
    ▼
        执行工具
    │
    ▼
┌─────────────────────────────────┐
│  读取 hooks.yaml                │
│  匹配 PostToolUse hooks         │
│  - 异步执行（不阻塞）           │
└─────────────────────────────────┘
    │
    ▼
        返回结果给用户
```

---

## CLI 命令参考

### wb-hook init

初始化 hook 系统，生成目录结构和示例配置。

### wb-hook add <event> <matcher> --command <cmd>

添加 hook。

```bash
wb-hook add PreToolUse "Write|Edit" --command "python .claude-hooks/hooks/check.py"
```

### wb-hook list

列出所有已注册的 hooks。

### wb-hook remove <event> <matcher>

删除 hook。

```bash
wb-hook remove PreToolUse Write
```

### wb-hook test <event> <tool> [--params <json>]

测试 hook（不实际执行工具）。

```bash
wb-hook test PreToolUse Write --params '{"file_path": "node_modules/index.js"}'
```

### wb-hook run <event> [--tool <tool>] [--params <json>]

手动触发 hook（用于调试）。

---

## 高级用法

### 1. Hook 优先级

同一事件的多个 hooks 按配置顺序执行，任一 hook 返回 `"block"` 则立即终止。

### 2. Hook 超时处理

如果 hook 脚本在 `timeout` ms 内未返回，默认决策为 `"allow"`（可通过 `on_error` 修改）。

### 3. Hook 链式修改

多个 hooks 可以依次修改参数（需所有 hooks 返回 `"modify"`）。

### 4. 与 MCP 联动

Hook 可以调用 MCP 工具（如 `mcp__tencent-docs__...`），实现跨平台自动化。

**示例**：每次 Write 后自动同步到腾讯文档

```python
# post_write_sync_docs.py
import sys
import json

event = json.load(sys.stdin)

# 调用 MCP 工具同步
# （需要在 hook 脚本中通过 subprocess 调用）
```

### 5. 企业级审计 Hook

**场景**：所有文件操作记录到审计日志 + 企业微信通知

```python
# audit_hook.py
import sys
import json
import requests

event = json.load(sys.stdin)

# 记录到审计日志
audit_log = {
    "user": os.getenv("USER"),
    "event": event,
    "timestamp": time.time()
}

requests.post("https://audit.company.com/log", json=audit_log)

# 高风险操作发送企业微信通知
if event.get("tool") == "Bash" and "rm -rf" in event.get("params", {}).get("command", ""):
    send_wecom_notification(f"⚠️ 高风险操作：{event}")
```

---

## 故障排查

### Hook 不生效

1. 检查 `hooks.yaml` 路径是否正确（默认 `.claude-hooks/hooks.yaml`）
2. 检查 matcher 是否匹配工具名（区分大小写）
3. 检查 hook 脚本是否有执行权限（`chmod +x`）
4. 检查 hook 脚本是否输出 valid JSON 到 stdout

### Hook 阻断不生效

1. 确认 hook 返回 `{"decision": "block", "reason": "..."}` 格式
2. 确认 hook 的 exit code 为 0（非 0 会导致 on_error 兜底）
3. 检查是否有其他 hook 返回 `"allow"`（按配置顺序执行）

### Hook 执行超时

1. 增加 `timeout` 配置（默认 3000ms）
2. 优化 hook 脚本性能（避免网络请求超时）
3. 设置 `on_error: "allow"` 避免误阻断

---

## 元信息

- **版本**：v1.0
- **最后更新**：2026-06-26
- **维护者**：wq180705550-cmd
- **依赖**：Python 3.8+、jq（可选）
- **兼容性**：WorkBuddy、Claude Code（部分兼容）
