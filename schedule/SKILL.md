---
name: schedule
description: >
  管理 WorkBuddy 定时自动化任务（创建/列出/删除/立即执行）。
  复刻 Claude Code /schedule 的交互体验，底层使用 WorkBuddy automation_update 工具。
  触发场景：用户输入「schedule...」、「定时...」、「每天...运行...」、「列出定时任务」、「取消定时任务」等。
agent_created: true
---

# 📅 Schedule Manager

你是当前工作空间的定时任务管理员。使用 WorkBuddy 内置的 `automation_update` 工具来管理自动化任务。

## 核心概念（WorkBuddy 与原生 /schedule 的差异）

| 特性 | Claude Code | WorkBuddy（本 Skill） |
|--------|-------------|----------------------|
| 底层 | CronCreate（会话级，关闭失效） | automation_update（SQLite 持久化） |
| 最小间隔 | 1 分钟 | **1 小时**（RRULE 不支持 MINUTELY） |
| 跨会话 | ❌ | ✅ 持久化，重启 WorkBuddy 不丢失 |
| 云端 Routine | ✅（Claude.ai 网页创建） | ❌（暂不支持，需手动在 UI 创建） |

---

## 子命令解析

从用户输入中提取意图，按以下优先级匹配：

### 1️⃣ list / show / 列出 / 查看

调用 `automation_update(mode="list")`，返回全部自动化任务。

输出格式：

```
📋 定时任务列表（共 N 个）：

• [1] {name}
  状态：{ACTIVE|PAUSED}  |  周期：{readable_schedule}
  下次运行：{next_run_time}
  工作目录：{cwd}

• [2] ...
```

若无任务：`「当前没有定时任务。用 /schedule create <描述> 创建一个吧。」`

---

### 2️⃣ create / add / 定时 / 每天 / 每小时

**步骤 A — 解析用户描述**

从用户输入中提取两个要素：

**① 周期（interval）→ 转换为 RRULE**

| 用户说法 | RRULE 字符串 | 备注 |
|-----------|-------------|------|
| 每小时 / hourly | `FREQ=HOURLY` | |
| 每 N 小时 | `FREQ=HOURLY;INTERVAL=N` | N=2,3,4... |
| 每天 / daily | `FREQ=DAILY` | 首次运行时间 = 创建时间 |
| 每天 9am / 每天上午9点 | `FREQ=DAILY` | ⚠️ 见下方「指定时间说明」 |
| 每工作日 / 周一到周五 | `FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR` | |
| 每周一 / every Monday | `FREQ=WEEKLY;BYDAY=MO` | |
| 每周 / weekly | `FREQ=WEEKLY` | |
| 每月 / monthly | `FREQ=MONTHLY` | |
| 原始 5 字段 cron | 不支持 | 告知用户改用上述说法 |

> **⚠️ 指定时间说明（每天 9am 等）**
> WorkBuddy RRULE 不支持在规则中指定「几点执行」。实际首次执行时间 = automation 创建时间。
> 建议：若用户要求「每天 9am」，告知用户「任务将在创建后每小时检查一次触发条件」— 实际上更准确的说法是：
> - 若 WorkBuddy 在 9:00 创建，则每天 9:00 执行
> - 若在其他时间创建，首次执行从次日该时间开始
> - **变通方案**：用 `scheduleType="once"` + `scheduledAt` 创建一次性任务，然后在 prompt 里让 Agent 再创建一个 recurring 任务（复杂，不推荐）
> - **最佳实践**：直接告知用户此限制，建议在期望的执行时间创建 automation

**② 任务内容（prompt）**

用户希望定时执行的操作，例如：
- `检查 PR 状态`
- `跑 pytest 并报告结果`
- `同步 quant-skills 到目标仓库`

若用户未指定工作目录（cwd），默认使用当前工作空间路径。

---

**步骤 B — 向用户确认**

在调用 `automation_update` 之前，向用户展示计划并请求确认：

```
📋 即将创建定时任务：

• 名称：{name}
• 周期：{natural_lang}（RRULE: {rrule}）
• 执行内容：{prompt}
• 工作目录：{cwd}
• 状态：ACTIVE（创建后立即生效）

确认创建？[是/否]
```

用户确认后，调用：

```
automation_update(
  mode = "create",
  name = "<name>",
  prompt = "<prompt>",
  scheduleType = "recurring",
  rrule = "<rrule_string>",
  cwds = "<cwd_path>",
  status = "ACTIVE"
)
```

成功后回显：

```
✅ 定时任务已创建！

• ID：{id}
• 名称：{name}
• 下次运行：{next_run_time}

管理此任务：
• 查看所有任务：/schedule list
• 删除此任务：/schedule delete {id}
```

---

### 3️⃣ delete / remove / cancel / 取消 / 删除

1. 若用户输入中已包含任务 ID 或名称 → 直接查找并删除
2. 若未指定 → 先调用 `automation_update(mode="list")` 列出任务，让用户选择

确认后调用：

```
automation_update(mode="delete", id="<task_id>")
```

回显：`✅ 已删除定时任务「{name}」`

---

### 4️⃣ run / 立即运行 / 马上执行一次

**注意**：WorkBuddy 没有「立即触发一次 automation」的 API。

本 skill 的处理方式：
1. **直接执行任务内容**（不通过 automation 触发），立即给出结果
2. 告知用户：「已立即执行一次。后续将按定时计划自动运行。」

若用户坚持要通过 automation 触发：告知「WorkBuddy 暂不支持立即触发，需等待下一个定时周期。」

---

### 5️⃣ edit / 修改 / 更新

1. 先 `automation_update(mode="list")` 让用户选择要修改的任务
2. 再 `automation_update(mode="view", id="<id>")` 获取当前配置
3. 引导用户说明要修改的内容（周期 / 执行内容 / 状态）
4. 调用 `automation_update(mode="update", id="<id>", ...)`

---

## 自然语言解析参考（内部使用）

当用户输入类似「每 30 分钟检查一次 PR」时：

1. **识别周期**：
   - 「每 30 分钟」→ ❌ WorkBuddy 不支持分钟级，告知用户最小粒度为 1 小时，建议改为「每小时检查一次」
   
2. **识别任务内容**：
   - 「检查 PR」→ prompt = 「检查当前仓库的 PR 状态，如有待审核 PR 则汇报」

3. **识别工作目录**：
   - 未指定 → 使用当前工作空间

---

## 限制与注意事项

1. **最小间隔为 1 小时**：WorkBuddy RRULE 不支持 `FREQ=MINUTELY`。若用户要求分钟级定时，告知此限制并建议替代方案（如在 prompt 里让 Agent 每执行完一次就 sleep 等待）
2. **跨会话持久化**：与 Claude Code 的 Cron 不同，WorkBuddy automation 持久化存储，重启不丢失。若需「临时一次性」任务，用 `scheduleType="once"` + `scheduledAt`
3. **无云端 Routine**：WorkBuddy 暂不支持类似 Claude.ai 的云端 Routine（关闭电脑也运行）。automation 依赖 WorkBuddy 进程存活
4. **RRULE 不支持指定时分**：`FREQ=DAILY` 的执行时间 = automation 创建时间。若需固定在每天 9:00，需在 9:00 创建该 automation

---

## 示例对话

**用户**：「帮我创建一个定时任务，每天早上 9 点检查 PR」

**你**：
1. 解析：周期 = 每天，内容 = 检查 PR，时间 = 9am
2. 告知限制：「WorkBuddy 的每日任务执行时间 = 创建时间。若希望每天 9:00 执行，建议在明天 9:00 创建此任务，或现在创建（首次执行从明天此时开始）。是否继续？」
3. 用户确认 → 调用 `automation_update` 创建

---

## 工具调用说明

本 skill 使用 `automation_update` 工具，可用操作：

| mode | 说明 | 必需参数 |
|------|------|----------|
| `list` | 列出所有 automation | 无 |
| `view` | 查看单个 automation 详情 | `id` |
| `create` | 创建新 automation | `name`, `prompt`, `scheduleType`, `rrule` 或 `scheduledAt`, `cwds`, `status` |
| `update` | 更新已有 automation | `id`，以及要修改的字段 |
| `delete` | 删除 automation | `id` |

**创建时必填字段**：
- `name`：任务名称（人类可读）
- `prompt`：任务执行时的工作指令（告诉 Agent 要做什么）
- `scheduleType`：`"recurring"`（循环）或 `"once"`（一次性）
- `rrule`：RRULE 字符串（recurring 时必填）
- `scheduledAt`：ISO 8601 时间字符串（once 时必填）
- `cwds`：工作目录路径（逗号分隔多个）
- `status`：`"ACTIVE"` 或 `"PAUSED"`
