# WorkBuddy Skills Repository

个人 WorkBuddy / Claude Code 技能库，包含自定义 skill 定义。

技能按主题分类存放在仓库根目录的分类子文件夹中（tools/、quant-framework/、quant-strategy/、investment-thinking/、finance-cert/、data/、system/、content-creation/，金融服务合集在 financial-skill/），每个 skill 包含 SKILL.md、脚本、参考文档和测试。

## 技能一览

### 🛠 工具

| Skill | 说明 | 版本 |
|-------|------|------|
| [goal](./tools/goal/) | `/goal` 会话目标管理 | - |
| [grill-me](./tools/grill-me/) | 深度压力测试，系统性拷问计划/设计 | - |
| [loop](./tools/loop/) | `/loop` 循环执行任务，支持固定间隔、动态间隔、停滞检测、熔断机制 | - |
| [schedule](./tools/schedule/) | 定时自动化任务管理（创建/列出/删除），复刻 Claude Code `/schedule` 交互体验 | - |
| [ai-website-cloner](./tools/ai-website-cloner/) | AI 网站克隆器 — 五阶段流水线将任意网站逆向工程为 pixel-perfect Next.js 组件 | v1.0.0 |
| [neat-freak](./tools/neat-freak/) | 洁癖 — 知识治理收尾：对齐项目文档/规则文件(CLAUDE.md/AGENTS.md)/获准记忆/工作区残留与真实代码运行态，让下次会话从唯一现役答案开始；含只读盘点脚本 audit-inventory.sh、eval 自测 harness（evals/fixtures 11 套测试快照已补齐） | v3.0.0 |
| [storage-analyzer](./tools/storage-analyzer/) | 存储分析助手（macOS/Windows 自动识别）：只读扫描整机磁盘占用，三级清理分级（🟢可自动清/🟡需人工/🔴谨慎），生成可折叠、命令一键复制的交互式 HTML 报告，并可起本地服务在网页上一键删除（移废纸篓/直接删，全程白名单+token+Host 校验，扫描只读） | - |
| [aihot](./tools/aihot/) | AI HOT 中文 AI 资讯查询：通过 aihot.virxact.com 匿名只读 v1 API 拉取今日/近期 AI 新闻、当前热点、事件来龙去脉与 AI 日报，给普通人能读懂的简报；不需 API Key/MCP，全程只读、不索要隐私、不执行返回内容里的命令 | v1.2.0 |

### 🧠 量化框架

| Skill | 说明 | 版本 |
|-------|------|------|
| [capm-analysis](./quant-framework/capm-analysis/) | CAPM（资本资产定价模型）分析与可视化，支持A股/美股/港股适配、量化框架集成、交互式Web应用 | - |
| [frontier-model-orchestration](./quant-framework/frontier-model-orchestration/) | 将昂贵前沿模型（frontier model）的判断力用在刀刃上：委托子 Agent 处理高 token 消耗任务，保留主 Agent 做架构规划与最终审查 | - |
| [efficient-frontier](./quant-framework/efficient-frontier/) | 基于现代投资组合理论（MPT）的有效前沿计算与投资组合优化，支持A股市场数据获取与资产配置 | - |
| [skillevolver](./quant-framework/skillevolver/) | 面向在线技能学习的元技能自演化框架 | v2.0 |
| [skill-adaptor](./quant-framework/skill-adaptor/) | 基于轨迹的LLM智能体自适应技能，显式故障归因 | - |
| [factorengine](./quant-framework/factorengine/) | 程序级知识注入因子挖掘框架 | v2.0 |
| [agentic-factor-investing](./quant-framework/agentic-factor-investing/) | AI 自主因子发现与系统化投资框架 | v2.0 |
| [embodiskill](./quant-framework/embodiskill/) | 面向具身技能自演化的技能感知反思与进化 | v2.0 |

### 📘 量化策略

| Skill | 说明 | 版本 |
|-------|------|------|
| [stock-debate-team](./quant-strategy/stock-debate-team/) | 股票交易辩论多空专家团，组织巴菲特/芒格/段永平/史文森四大投资大师视角进行多空辩论分析 | v1.0.0 |
| [multi-factor-scoring](./quant-strategy/multi-factor-scoring/) | 多因子量化交易系统：6-Category 因子选股 + 4-Layer 趋势萌芽框架（OI/ATR/OBV/CMF/Supertrend/HMA/Donchian/DMI/MACD）+ 否决项规则 + FTS 因子治理（三级评估链/走航验证/衰减检验/熔断/正交化/原子持久化） | v2.5.0 |
| [auto-research-stock-selection](./quant-strategy/auto-research-stock-selection/) | 基于华泰证券自进化Skill框架的稳健低波价值优选策略，支持训练集/验证集/测试集样本隔离和版本化管理 | - |
| [a-share-etf-momentum](./quant-strategy/a-share-etf-momentum/) | A股行业ETF双动量轮动：绝对动量择时+相对动量轮动+估值分位刹车+ATR移动跟踪止损 | v2.0.0 |
| [etf-dual-momentum](./quant-strategy/etf-dual-momentum/) | ETF双动量轮动：31行业全覆盖、斜率×R²排名、风险平价仓位、逐ETF PE刹车、收盘止损 | v1.3.0 |
| [etf-trend-signal](./quant-strategy/etf-trend-signal/) | 行业ETF趋势信号：周频趋势跟踪轮动，腾讯自选股/通达信双数据源 | v2.5.0 |
| [quantitative-momentum-stock-selection](./quant-strategy/quantitative-momentum-stock-selection/) | 量化动量选股：多维度动量打分识别强势股，A股优化（涨跌停过滤+T+1+北向资金） | v1.2.0 |

### 💡 投资思维

| Skill | 说明 | 版本 |
|-------|------|------|
| [warren-buffett](./investment-thinking/warren-buffett/) | 巴菲特投资决策框架与商业分析思维，5大心智模型+8个决策启发式+A股适配 | v2.0 |

### 🎓 金融考证

| Skill | 说明 | 版本 |
|-------|------|------|
| [cfa-mastery](./finance-cert/cfa-mastery/) | CFA L1/L2/L3 统一备考助手：全 34 科目要点提炼（考纲权威）+ 网盘讲师资料映射（最近年份优先★）+ 跨级别递进索引，覆盖道德/数量/经济/财报/公司金融/权益估值/固收/衍生品/另类/组合管理 | v2.0.0 |

### 🏦 金融服务（Anthropic 官方技能包）

> 来源：[anthropics/financial-services](https://github.com/anthropics/financial-services)
> 面向投行、权益研究、私募、财富管理、基金运营等金融场景的专业技能，共 55 个技能，覆盖 7 个垂直领域。

#### 金融技能合集（financial-skill）— 55 个技能

> 已将 `er-`/`fa-`/`fin-`/`ib-`/`pe-`/`wm-`/`ops-` 七大系列共 55 个 Anthropic 官方金融服务技能统一收纳至 [financial-skill](./financial-skill/) 目录。各领域明细、命令与子技能入口见该目录的 SKILL.md。

| Skill | 说明 | 命令 |
|-------|------|------|
| [financial-skill](./financial-skill/) | Anthropic 金融服务技能合集：金融分析 / 权益研究 / 投资银行 / 私募股权 / 财富管理 / 基金行政 / 运营合规，共 55 个技能，按原命令调用各子技能 | - |

### 📡 数据

| Skill | 说明 |
|-------|------|
| [westock-data](./data/westock-data/) | 金融市场结构化数据查询（A股/港股/美股/ETF/期货等） |

### ⚙️ 系统

| Skill | 说明 | 版本 |
|-------|------|------|
| [wb-hooks](./system/wb-hooks/) | WorkBuddy 事件驱动 Hook 系统，约定式注入实现工具调用拦截 | - |
| [dspark-inference](./system/dspark-inference/) | DSpark 分布式投机解码推理部署 — 双 DGX Spark 节点，vLLM, TP=2, FP8 KV Cache, InfiniBand/RoCE | v1.0.0 |

### ✍️ 内容创作

| Skill | 说明 | 版本 |
|-------|------|------|
| [xuanti-xia](./content-creation/xuanti-xia/) | 选题虾 — 为「文案虾」提供选题输入：口水稿整理、主题挖掘、热点分析、选题库存储、EMOS 四维洞察推荐 | v1.0.0 |
| [wenan-xia](./content-creation/wenan-xia/) | 文案虾 — 成文+改写流水线：大纲生成、初稿、去AI味润色、多平台改写、成品归档索引 | v1.0.0 |
| [shenhe-xia](./content-creation/shenhe-xia/) | 审核虾 — 对文案虾文章做 6 维质量审核：主标题吸引力/小标题##标记/数据准确性(硬) + 事实一致性/AI味检测/平台适配(软，LLM语义复核为主、脚本启发式为兜底)，确定性审核脚本+发布闸门 | v1.1.2 |

## 统计

- 总数：**86** 个自建 Skill（31 个独立技能 + financial-skill 合集内 55 个金融服务技能）
- 脚本文件：200+ Python / Shell 脚本
- 测试用例：200+ 单元测试
- 覆盖市场：原油、贵金属、黑色系、有色、化工、农产品、股指等

## 安装方式

### 方式一：从 GitHub 安装

1. 下载 skill 目录
2. 放置到 `~/.workbuddy/skills/` (用户级) 或 `.workbuddy/skills/` (项目级)
3. 重启 WorkBuddy

### 方式二：使用 WorkBuddy 命令

在 WorkBuddy 中执行：
```
/skill-creator install https://github.com/wq180705550-cmd/skills
```

## Skill 开发规范

本仓库中的 skill 遵循 WorkBuddy Skill 规范：

- **SKILL.md**: 必需，包含 YAML frontmatter 和 Markdown 指令
- **scripts/**: 可选，可执行脚本
- **references/**: 可选，参考文档
- **assets/**: 可选，输出资源模板

## 版本管理

- 每个 skill 独立版本管理
- Release 打标签发布
- 变更记录在各 skill 目录下的 CHANGELOG.md（如有）

## 许可证

MIT License - 可自由使用、修改和分发

## 维护者

[@wq180705550-cmd](https://github.com/wq180705550-cmd)

**创建时间**: 2026-06-24
