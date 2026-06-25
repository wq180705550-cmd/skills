---
name: efficient-frontier
description: >
  将昂贵前沿模型（frontier model）的判断力用在刀刃上：把可并行、可重复、
  高 token 消耗的研究/编码/测试工作委托给更便宜的子 Agent，
  保留架构规划、优先级判断、歧义消解、风险决策、结果综合和最终审查
  给主 Agent。适用于多步骤复杂任务的成本优化。
  触发场景：任务涉及大量研究扫描、多文件编辑、并行测试、或用户提到
  「节省 token」、「并行处理」、「子 Agent 分工」等。
agent_created: true
---

# Efficient Frontier — 高效前沿模型编排

将昂贵模型的能力用在判断上，把体力活交给便宜的子 Agent。

## 核心原则

> **用前沿模型做指挥和审查，用便宜 Agent 做研究和执行。**

昂贵 token 应该花在：
- 架构决策
- 优先级判断
- 歧义消解
- 风险评估
- 结果综合
- 最终审查

可以委托出去的：
- 代码库扫描、文件搜索
- 文档提取、资料搜集
- 重复性编码、机械化编辑
- 测试执行、日志归纳
- 失败聚类、Bug 复现

---

## 工作流

### 第 1 步：识别不可委托的决策

以下必须由主 Agent（frontier model）完成：

| 决策类型 | 说明 |
|----------|------|
| 架构规划 | 模块划分、接口设计、依赖选择 |
| 优先级 | 先做什么后做什么 |
| 歧义消解 | 需求不明确时的判断 |
| 风险评估 | 哪些地方容易出错 |
| 结果综合 | 把子 Agent 的输出整合成最终答案 |
| 最终审查 | 验证结果是否正确 |

### 第 2 步：识别可委托的工作

以下可以安全地委托给子 Agent：

| 工作类型 | 示例 |
|----------|------|
| 研究扫描 | 扫描代码库、搜索文档、提取 API 用法 |
| 仓库盘点 | 列出所有路由、查找所有 TODO、统计测试覆盖 |
| 浏览器/测试 | 运行测试套件、截图对比、日志过滤 |
| 编码（有界） | 明确范围内的补丁、重构、样板代码生成 |
| 机械化编辑 | 批量重命名、格式统一、依赖更新 |

### 第 3 步：并行派发子 Agent

使用 WorkBuddy 的 `Agent` 工具并行派发独立任务。在同一轮 response 中发起多个 `Agent` 调用实现并行。

**Agent 工具关键参数**：

| 参数 | 说明 | 示例 |
|------|------|------|
| `description` | 简短描述（3-5 词），用于 UI 显示 | `"扫描 API 路由定义"` |
| `prompt` | 完整任务指令（即 handoff packet） | 见下方模板 |
| `subagent_type` | 子 Agent 类型 | `"general-purpose"` 或 `"Explore"` |
| `model` | 子 Agent 使用的模型 | `"lite"`（省钱）/`"default"`/`"reasoning"` |
| `run_in_background` | 是否后台运行 | `true`（并行时必须） |

**Handoff Packet 模板**（放入 `prompt` 参数）：

```
## 任务
[明确描述要做什么]

## 范围
- 包含：[目录/文件/主题]
- 不包含：[明确边界]

## 上下文
- 工作目录：{cwd}
- 相关文件：[列出关键文件]
- 搜索关键词：[如有]

## 返回格式
[期望的输出结构，例如：Markdown 表格 / JSON / 文件列表]

## 验证
[子 Agent 完成后应自行运行的验证步骤]

## 停止条件（遇到以下情况立即停止并上报）
1. [条件 1]
2. [条件 2]
```

**实际调用示例**（主 Agent 执行，以下为伪代码用于说明参数结构，实际工具调用由 AI 自动完成）：

```python
# 并行派发两个子 Agent
Agent(
    description="扫描 API 路由",
    prompt="""## 任务
扫描 src/routes/ 下所有路由定义。

## 范围
- 包含：src/routes/**/*.py
- 不包含：测试文件

## 返回格式
Markdown 表格：| 路径 | 方法 | 处理函数 |

## 验证
对照实际文件确认每个路由都存在

## 停止条件
1. 找不到路由文件立即上报""",
    subagent_type="Explore",
    model="lite",
    run_in_background=True
)

Agent(
    description="提取数据库 Schema",
    prompt="""## 任务
读取 src/models/ 下所有模型定义，列出每个模型的字段。

## 返回格式
Markdown 表格：| 模型名 | 字段名 | 类型 | 是否必填 |""",
    subagent_type="Explore",
    model="lite",
    run_in_background=True
)
# 两个 Agent 并行运行，主 Agent 继续后续工作
```

**注意**：`run_in_background=True` 时，子 Agent 完成后通过 `SendMessage` 回传结果；主 Agent 用 `TaskOutput` 工具获取输出。

### 第 4 步：要求紧凑返回

子 Agent 的返回必须包含：
- **发现**：关键结论
- **变更文件**：如有编辑，列出文件路径
- **运行命令**：执行了哪些命令
- **残余风险**：还有什么没解决
- **触发停止条件**：是否遇到了 handoff 中的停止条件
- **需要主 Agent 决策的事项**：哪些需要人工判断

### 第 5 步：集中整合与审查

在呈现结果之前：
1. 重新打开重要的引用文件核实
2. 检查高风险 diff
3. 重新运行或抽查关键的验证步骤
4. 如果子 Agent 之间有分歧，由主 Agent 裁决

---

## 完整工作流示例

### 场景：重构 API 层并添加测试

**主 Agent（frontier model）负责**：
1. 决策：是否保持向后兼容
2. 规划：哪些路由需要重构、测试策略
3. 审查：子 Agent 返回的代码是否正确

**子 Agent A（研究扫描，`model="lite"`）**：
```python
Agent(
    description="扫描现有 API 路由",
    prompt="""## 任务
列出 src/routes/ 下所有路由的路径、HTTP 方法、处理函数、是否已有测试。

## 范围
- 包含：src/routes/**/*.py
- 不包含：src/tests/ 目录

## 返回格式
Markdown 表格：
| 文件 | 路由路径 | 方法 | 处理函数 | 已有测试？ |

## 验证
每个列出的路由都在文件中实际存在

## 停止条件
1. 找不到 src/routes/ 目录立即上报
2. 发现非 .py 文件立即跳过并说明""",
    subagent_type="Explore",
    model="lite",
    run_in_background=True
)
```

**子 Agent B（测试生成，`model="default"`）**：
```python
Agent(
    description="为缺失测试的路由生成测试用例",
    prompt="""## 任务
根据子 Agent A 返回的路由列表，为没有测试的路由生成 pytest 用例。

## 上下文
等待子 Agent A 完成并返回路由列表。

## 返回格式
完整的 test_*.py 文件内容，可直接写入。

## 验证
生成的测试可以用 pytest 运行（语法正确）。

## 停止条件
1. 如果某个路由逻辑过于复杂（需要 mock 外部服务），标注出来交给主 Agent 决策
2. 生成的测试语法错误，修复一次后仍然失败，上报""",
    subagent_type="general-purpose",
    model="default",
    run_in_background=True
)
```

**主 Agent 整合结果**：
1. 等待两个子 Agent 完成（通过 `TaskOutput` 获取结果）
2. 审查子 Agent A 的路由列表是否完整（抽查 2-3 个文件）
3. 审查子 Agent B 生成的测试是否覆盖了关键路径
4. 如有分歧或遗漏，派发补丁子 Agent 修复
5. 最终输出：重构后的代码 + 测试文件

---

## 子 Agent 结果解析与整合

主 Agent 收到子 Agent 返回后，按以下流程处理：

1. **完整性检查**：返回结果是否包含了 handoff packet 中要求的所有字段？
2. **证据核实**：子 Agent 声称「X 文件存在 Y 函数」，主 Agent 重新打开 X 文件核实
3. **交叉验证**：如果多个子 Agent 涉及同一区域，对比它们的结论是否一致
4. **风险标注**：子 Agent 标注的「残余风险」逐一评估，决定是否需要额外 Agent 处理
5. **整合输出**：将所有子 Agent 的结果合成为最终答案，明确标注哪些部分来自哪个子 Agent

**禁止行为**：
- 直接把子 Agent 的原始返回转发给用户（必须经审查整合）
- 子 Agent 之间存在矛盾时，不调查就选一个

---

## 常用场景

### 研究任务
- 委托：broad repo scan、文档提取、源码对比
- 保留：判断哪些信息重要

### 编码任务
- 委托：有界补丁、重构、机械化编辑（文件归属清晰时）
- 保留：集成和审查

### 测试任务
- 委托：运行单元测试、浏览器流、截图、日志归纳
- 保留：选择验证策略和脚本

### 调试任务
- 委托：独立 Agent 分别追查不同理论、日志、复现路径
- 保留：最终诊断

---

## 停止条件（子 Agent 遇到以下情况应停止并上报）

在 handoff packet 中写入停止条件，子 Agent 遇到时应停止并上报：

- 实际代码与 handoff 中的假设不符
- 验证命令失败两次（经过合理修复后）
- 工作似乎需要超出分配范围的文件
- Agent 无法为其主张提供具体证据

---

## 守护规则

1. **不要委托即时阻塞项**：如果下一步依赖于某个结果，不要把它委托出去
2. **不要多 Agent 同时编辑同一文件**：避免冲突
3. **高风险时不要盲目信任子 Agent 结论**：亲自检查重要证据
4. **不要声称普遍节省**：这种模式在可并行化的场景下效果最好

---

## WorkBuddy 实现说明

在 WorkBuddy 中，本 skill 通过以下工具实现子 Agent 编排：

| 操作 | 工具 |
|------|------|
| 派发子 Agent | `Agent` 工具（subagent_type: general-purpose / Explore / Plan） |
| 并行派发 | 在同一 response 中发起多个 `Agent` 调用 |
| 子 Agent 返回 | 通过 `SendMessage` 或直接返回结果 |
| 集中审查 | 主 Agent 收到所有结果后整合 |

**模型选择建议**：
- 主 Agent：使用强模型（`"default"` 或 `"reasoning"`，在主 Agent 配置中设置）
- 子 Agent：在 `Agent` 调用中指定 `model="lite"` 以节省成本（适用于研究扫描、机械化编辑等低判断任务）
- 子 Agent 需要复杂推理时：指定 `model="default"` 或 `model="reasoning"`

---

## 常见问题排查

### 子 Agent 返回结果质量差

**原因**：handoff packet 不够具体，子 Agent 不知道期望的输出格式。

**修复**：在 handoff packet 的「返回格式」部分给出具体模板或示例。

### 子 Agent 编辑了不该碰的文件

**原因**：「范围」部分定义不清晰。

**修复**：在 handoff packet 中明确列出「不包含」的文件/目录。

### 成本没有节省

**原因**：子 Agent 也用了强模型，或 handoff packet 过于复杂导致子 Agent token 消耗也很大。

**修复**：子 Agent 用 `model="lite"`；handoff packet 保持简洁；只委托真正可并行的工作。

---

## 默认表述

启动本 skill 时，向用户说明编排计划：

> 「我将使用主 Agent 作为指挥者和审查者，使用更便宜的子 Agent 处理
> 高 token 消耗的研究、编码或测试工作，让昂贵的 token 花在判断、
> 综合和最终质量上。
>
> 计划派发 N 个子 Agent 并行处理：[列出每个子 Agent 的任务]。
> 预计节省约 X% 的 token（仅估算，实际取决于任务可并行程度）。」
