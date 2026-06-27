# WorkBuddy Skills Repository

个人 WorkBuddy / Claude Code 技能库，包含自定义 skill 定义。

技能存放在仓库根目录下，每个 skill 包含 SKILL.md、脚本、参考文档和测试。

## 技能一览

### 📈 能源
| Skill | 说明 | 版本 |
|-------|------|------|
| [crude-oil-daily-news](./crude-oil-daily-news/) | 国际原油每日资讯（WTI/布伦特），四层分析框架+20项技术指标 | v9.0 |
| [energy-chain-analysis](./energy-chain-analysis/) | 能源产业链整体分析（SC/BU/FU/LU/PG），五层量化打分+七步决策法 | v2.19.0 |

### 💎 贵金属
| Skill | 说明 | 版本 |
|-------|------|------|
| [precious-metals-daily-news](./precious-metals-daily-news/) | 贵金属每日资讯（黄金/白银/铂钯），19项技术指标+右侧交易原则 | v4.3.0 |
| [precious-metals-data-validation](./precious-metals-data-validation/) | 贵金属数据标准化采集与验证，多源交叉校验 | v2.0.0 |
| [precious-metals-trading-decision](./precious-metals-trading-decision/) | 三层架构贵金属交易决策（宏观→载体→多周期），R1-R5 Regime诊断 | v3.0.0 |

### 🚜 期货
| Skill | 说明 | 版本 |
|-------|------|------|
| [futures-industry-chain-analysis](./futures-industry-chain-analysis/) | 12大产业链自动化分析，自下而上+置信度优先，67+品种 | v2.9.1 |
| [futures-trading-analysis](./futures-trading-analysis/) | 多角色辩论式交易分析，12专业Agent，单品/产业链双模式 | v1.0 |

### 📊 数据
| Skill | 说明 | 版本 |
|-------|------|------|
| [exchange-futures-data](./exchange-futures-data/) | 中国五大期货交易所（DCE/SHFE/CZCE/CFFEX/GFEX）官方数据采集 | - |

### 🛠 工具
| Skill | 说明 |
|-------|------|
| [goal](./goal/) | `/goal` 会话目标管理 |
| [grill-me](./grill-me/) | 深度压力测试，系统性拷问计划/设计 |
| [loop](./loop/) | `/loop` 循环执行任务，支持固定间隔、动态间隔、停滞检测、熔断机制 |
| [schedule](./schedule/) | 定时自动化任务管理（创建/列出/删除），复刻 Claude Code `/schedule` 交互体验 |

### 🧠 量化框架
| Skill | 说明 | 版本 |
|-------|------|------|
| [capm-analysis](./capm-analysis/) | CAPM（资本资产定价模型）分析与可视化，支持A股/美股/港股适配、量化框架集成、交互式Web应用 | - |
| [frontier-model-orchestration](./frontier-model-orchestration/) | 将昂贵前沿模型（frontier model）的判断力用在刀刃上：委托子 Agent 处理高 token 消耗任务，保留主 Agent 做架构规划与最终审查 | - |
| [efficient-frontier](./efficient-frontier/) | 基于现代投资组合理论（MPT）的有效前沿计算与投资组合优化，支持A股市场数据获取与资产配置 | - |
| [skillevolver](./skillevolver/) | 面向在线技能学习的元技能自演化框架 | v2.0 |
| [skill-adaptor](./skill-adaptor/) | 基于轨迹的LLM智能体自适应技能，显式故障归因 | - |
| [factorengine](./factorengine/) | 程序级知识注入因子挖掘框架 | v2.0 |
| [agentic-factor-investing](./agentic-factor-investing/) | AI 自主因子发现与系统化投资框架 | v2.0 |
| [embodiskill](./embodiskill/) | 面向具身技能自演化的技能感知反思与进化 | v2.0 |

### 📘 量化策略
| Skill | 说明 |
|-------|------|
| [multi-factor-scoring](./multi-factor-scoring/) | 多因子量化交易系统，支持因子打分、回测和模拟 |
| [auto-research-stock-selection](./auto-research-stock-selection/) | 基于华泰证券自进化Skill框架的稳健低波价值优选策略，支持训练集/验证集/测试集样本隔离和版本化管理 |

### 💡 投资思维
| Skill | 说明 | 版本 |
|-------|------|------|
| [warren-buffett](./warren-buffett/) | 巴菲特投资决策框架与商业分析思维，5大心智模型+8个决策启发式+A股适配 | v2.0 |

### 🏦 金融服务（Anthropic 官方技能包）

> 来源：[anthropics/financial-services](https://github.com/anthropics/financial-services)
> 面向投行、权益研究、私募、财富管理、基金运营等金融场景的专业技能，共 55 个技能，覆盖 7 个垂直领域。

#### 金融分析（Financial Analysis）— 13 个技能

| Skill | 说明 | 命令 |
|-------|------|------|
| [fin-3-statement-model](./fin-3-statement-model/) | 三表联动财务模型模板 | `/3-statement-model` |
| [fin-audit-xls](./fin-audit-xls/) | Excel模型审计（公式追溯/硬编码检测/平衡校验） | `/debug-model` |
| [fin-clean-data-xls](./fin-clean-data-xls/) | Excel表格数据标准化清洗 | - |
| [fin-competitive-analysis](./fin-competitive-analysis/) | 竞争格局与市场定位分析 | `/competitive-analysis` |
| [fin-comps-analysis](./fin-comps-analysis/) | 可比公司分析，输出交易倍数 | `/comps` |
| [fin-dcf-model](./fin-dcf-model/) | DCF估值（含WACC计算、敏感性分析） | `/dcf` |
| [fin-deck-refresh](./fin-deck-refresh/) | 演示文稿嵌入图表/表格重新链接刷新 | - |
| [fin-ib-check-deck](./fin-ib-check-deck/) | 演示文稿错误与一致性校验 | - |
| [fin-lbo-model](./fin-lbo-model/) | 杠杆收购模型搭建 | `/lbo` |
| [fin-ppt-template-creator](./fin-ppt-template-creator/) | 创建可复用的企业品牌PPT模板 | `/ppt-template` |
| [fin-pptx-author](./fin-pptx-author/) | 无头模式生成.pptx文件 | - |
| [fin-xlsx-author](./fin-xlsx-author/) | 无头模式生成.xlsx文件 | - |
| [fin-skill-creator](./fin-skill-creator/) | 新技能创建引导 | - |

#### 权益研究（Equity Research）— 9 个技能

| Skill | 说明 | 命令 |
|-------|------|------|
| [er-catalyst-calendar](./er-catalyst-calendar/) | 覆盖标的催化剂事件跟踪 | `/catalysts` |
| [er-earnings-analysis](./er-earnings-analysis/) | 财报发布后季度更新报告 | `/earnings` |
| [er-earnings-preview](./er-earnings-preview/) | 财报前情景分析、核心指标预测 | `/earnings-preview` |
| [er-idea-generation](./er-idea-generation/) | 股票筛选与投研思路生成 | `/screen` |
| [er-initiating-coverage](./er-initiating-coverage/) | 机构级首次覆盖报告 | `/initiate` |
| [er-model-update](./er-model-update/) | 财务模型更新（录入新数据） | `/model-update` |
| [er-morning-note](./er-morning-note/) | 晨会会议纪要、交易思路整理 | `/morning-note` |
| [er-sector-overview](./er-sector-overview/) | 行业全景与主题研究报告 | `/sector` |
| [er-thesis-tracker](./er-thesis-tracker/) | 投资逻辑跟踪与更新 | `/thesis` |

#### 投资银行（Investment Banking）— 9 个技能

| Skill | 说明 | 命令 |
|-------|------|------|
| [ib-buyer-list](./ib-buyer-list/) | 搭建战略/财务买方清单 | `/buyer-list` |
| [ib-cim-builder](./ib-cim-builder/) | 起草保密信息备忘录（CIM） | `/cim` |
| [ib-datapack-builder](./ib-datapack-builder/) | 从CIM、申报文件构建数据包 | - |
| [ib-deal-tracker](./ib-deal-tracker/) | 跟踪在途交易、里程碑、待办事项 | `/deal-tracker` |
| [ib-merger-model](./ib-merger-model/) | 并购交易 accretion/dilution 分析 | `/merger-model` |
| [ib-pitch-deck](./ib-pitch-deck/) | 推介书模板自动填充数据 | - |
| [ib-process-letter](./ib-process-letter/) | 投标指引、交易流程函件起草 | `/process-letter` |
| [ib-strip-profile](./ib-strip-profile/) | 生成推介书用单页公司 profile | `/one-pager` |
| [ib-teaser](./ib-teaser/) | 生成匿名单页公司推介函 | `/teaser` |

#### 私募股权（Private Equity）— 10 个技能

| Skill | 说明 | 命令 |
|-------|------|------|
| [pe-ai-readiness](./pe-ai-readiness/) | 被投企业AI能力评估 | `/ai-readiness` |
| [pe-dd-checklist](./pe-dd-checklist/) | 分工作流尽职调查清单生成 | `/dd-checklist` |
| [pe-dd-meeting-prep](./pe-dd-meeting-prep/) | 管理层访谈、专家访谈准备材料 | `/dd-prep` |
| [pe-deal-screening](./pe-deal-screening/) | inbound CIM/推介函快速pass/fail筛查 | `/screen-deal` |
| [pe-deal-sourcing](./pe-deal-sourcing/) | 项目挖掘、CRM匹配、创始人触达函起草 | `/source` |
| [pe-ic-memo](./pe-ic-memo/) | 投资决策委员会备忘录起草 | `/ic-memo` |
| [pe-portfolio-monitoring](./pe-portfolio-monitoring/) | 被投企业KPI跟踪与偏差分析 | `/portfolio` |
| [pe-returns-analysis](./pe-returns-analysis/) | IRR/MOIC敏感性分析表 | `/returns` |
| [pe-unit-economics](./pe-unit-economics/) | ARR cohorts、LTV/CAC、净留存分析 | `/unit-economics` |
| [pe-value-creation-plan](./pe-value-creation-plan/) | 投后100天计划、EBITDA提升路径 | `/value-creation` |

#### 财富管理（Wealth Management）— 6 个技能

| Skill | 说明 | 命令 |
|-------|------|------|
| [wm-client-report](./wm-client-report/) | 客户业绩报告生成 | `/client-report` |
| [wm-client-review](./wm-client-review/) | 客户会议准备：业绩表现、沟通要点 | `/client-review` |
| [wm-financial-plan](./wm-financial-plan/) | 退休、教育、estate、现金流规划方案 | `/financial-plan` |
| [wm-investment-proposal](./wm-investment-proposal/) | 潜在客户投资方案建议书 | `/proposal` |
| [wm-portfolio-rebalance](./wm-portfolio-rebalance/) | 配置偏离分析、税务优化再平衡 | `/rebalance` |
| [wm-tax-loss-harvesting](./wm-tax-loss-harvesting/) | 税损harvest机会识别、洗售规则管理 | `/tlh` |

#### 基金行政（Fund Admin）— 6 个技能

| Skill | 说明 | 命令 |
|-------|------|------|
| [fa-accrual-schedule](./fa-accrual-schedule/) | 应计项计提、roll-forward计算 | - |
| [fa-break-trace](./fa-break-trace/) | 总账对账、差异追溯 | - |
| [fa-gl-recon](./fa-gl-recon/) | 总账对账、差异追溯、sign-off路由 | - |
| [fa-nav-tieout](./fa-nav-tieout/) | 基金NAV核对 | - |
| [fa-roll-forward](./fa-roll-forward/) | 应计项roll-forward计算 | - |
| [fa-variance-commentary](./fa-variance-commentary/) | 财务数据偏差说明撰写 | - |

#### 运营合规（Operations）— 2 个技能

| Skill | 说明 | 命令 |
|-------|------|------|
| [ops-kyc-doc-parse](./ops-kyc-doc-parse/) | 开户文档解析、规则引擎匹配 | - |
| [ops-kyc-rules](./ops-kyc-rules/) | KYC合规筛查规则 | - |

### 📡 数据
| Skill | 说明 |
|-------|------|
| [westock-data](./westock-data/) | 金融市场结构化数据查询（A股/港股/美股/ETF/期货等） |

### ⚙️ 系统
| Skill | 说明 |
|-------|------|
| [wb-hooks](./wb-hooks/) | WorkBuddy 事件驱动 Hook 系统，约定式注入实现工具调用拦截 |

## 统计

- 总数：**79** 个自建 Skill
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
