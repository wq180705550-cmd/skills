---
name: financial-skill
version: 1.0.0
description: >-
  Anthropic 金融服务官方技能合集 — 统一收纳金融分析（Financial Analysis）、
  权益研究（Equity Research）、投资银行（Investment Banking）、
  私募股权（Private Equity）、财富管理（Wealth Management）、
  基金行政（Fund Admin）、运营合规（Operations）七大领域的 55 个专业技能。
  按原命令调用各子技能，子技能路径现在位于 financial-skill/ 目录下。
agent_created: true
user_invocable: true
triggers:
  - 金融服务
  - 投行
  - 估值
  - 财报
  - 私募
  - 财富管理
  - 基金行政
  - 财务模型
  - 运营合规
  - KYC
  - financial analysis
  - 三表模型
  - DCF
  - 并购
  - 尽职调查
---

# financial-skill — Anthropic 金融服务技能合集

> 来源：[anthropics/financial-services](https://github.com/anthropics/financial-services)
> 面向投行、权益研究、私募、财富管理、基金运营、运营合规等金融场景的专业技能，共 55 个技能，覆盖 7 个垂直领域。
> 本目录将原先散落在仓库根目录的 `er-` / `fa-` / `fin-` / `ib-` / `pe-` / `wm-` / `ops-` 系列统一收纳，便于管理与分发。

## 使用方式

- 每个子技能保持独立的 `SKILL.md` 与脚本，按原 `/command` 调用即可。
- 子技能路径现为 `financial-skill/<skill-name>/`，例如 `financial-skill/fin-dcf-model/`。
- 各子技能的命令（如 `/dcf`、`/lbo`、`/comps`）不变。

## 目录结构

```
financial-skill/
├── fin-*   金融分析（Financial Analysis）— 13 个技能
├── er-*    权益研究（Equity Research）— 9 个技能
├── ib-*    投资银行（Investment Banking）— 9 个技能
├── pe-*    私募股权（Private Equity）— 10 个技能
├── wm-*    财富管理（Wealth Management）— 6 个技能
├── fa-*    基金行政（Fund Admin）— 6 个技能
└── ops-*   运营合规（Operations）— 2 个技能
```

## 技能清单

### 金融分析（Financial Analysis）— 13 个技能

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

### 权益研究（Equity Research）— 9 个技能

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

### 投资银行（Investment Banking）— 9 个技能

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

### 私募股权（Private Equity）— 10 个技能

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

### 财富管理（Wealth Management）— 6 个技能

| Skill | 说明 | 命令 |
|-------|------|------|
| [wm-client-report](./wm-client-report/) | 客户业绩报告生成 | `/client-report` |
| [wm-client-review](./wm-client-review/) | 客户会议准备：业绩表现、沟通要点 | `/client-review` |
| [wm-financial-plan](./wm-financial-plan/) | 退休、教育、estate、现金流规划方案 | `/financial-plan` |
| [wm-investment-proposal](./wm-investment-proposal/) | 潜在客户投资方案建议书 | `/proposal` |
| [wm-portfolio-rebalance](./wm-portfolio-rebalance/) | 配置偏离分析、税务优化再平衡 | `/rebalance` |
| [wm-tax-loss-harvesting](./wm-tax-loss-harvesting/) | 税损harvest机会识别、洗售规则管理 | `/tlh` |

### 基金行政（Fund Admin）— 6 个技能

| Skill | 说明 | 命令 |
|-------|------|------|
| [fa-accrual-schedule](./fa-accrual-schedule/) | 应计项计提、roll-forward计算 | - |
| [fa-break-trace](./fa-break-trace/) | 总账对账、差异追溯 | - |
| [fa-gl-recon](./fa-gl-recon/) | 总账对账、差异追溯、sign-off路由 | - |
| [fa-nav-tieout](./fa-nav-tieout/) | 基金NAV核对 | - |
| [fa-roll-forward](./fa-roll-forward/) | 应计项roll-forward计算 | - |
| [fa-variance-commentary](./fa-variance-commentary/) | 财务数据偏差说明撰写 | - |

### 运营合规（Operations）— 2 个技能

| Skill | 说明 | 命令 |
|-------|------|------|
| [ops-kyc-doc-parse](./ops-kyc-doc-parse/) | 开户文档解析、规则引擎匹配 | - |
| [ops-kyc-rules](./ops-kyc-rules/) | KYC合规筛查规则 | - |

## 说明

- 本目录仅作统一收纳与索引，不修改任何子技能的内部实现。
- 调用时直接使用对应子技能原命令；如需整体定位，可检索本目录 SKILL.md 的技能清单。
