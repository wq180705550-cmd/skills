---
name: wb-hooks
description: >
  WorkBuddy 事件驱动 Hook 系统 — 复刻 Claude Code /hook 体验。
  支持 PreToolUse（拦截/修改）、PostToolUse（记录/审计）、Stop（清理/上报）
  三种生命周期事件，通过 hooks.yaml 配置匹配器与执行脚本，
  实现自动阻断、参数改写、审计日志、会话级清理等企业级工作流。
when_to_use:
  - "创建 hook" / "hook add"
  - "列出 hook" / "hook list"
  - "禁止写入 node_modules" / "禁止删除 .env"
  - "每次 Read 后记录日志"
  - "会话结束时自动清理临时文件"
  - "PreToolUse" / "PostToolUse" / "Stop"
disable-model-invocation: false
---

# 🪝 WorkBuddy Hook System (wb-hooks)

复刻 Claude Code `/hook` 的事件驱动钩子系统。

---

## 核心概念

| Claude Code | WorkBuddy 实现 |
|-------------|---------------|
| `/hook` 命令 | `wb-hook` CLI（本 skill 提供） |
| 事件（PreToolUse / PostToolUse / Stop） | 通过 skill 指令 + 包装脚本模拟 |
| Matcher（工具名匹配） | 正则 / 精确匹配，配置在 `hooks.yaml` |
| Hook script | 任意可执行文件（Python / Bash / Node） |
| Decision（allow / block / modify） | exit code + stdout JSON |

---

## 快速开始

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
