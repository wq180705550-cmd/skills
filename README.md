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

### 🔩 期货
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
| [efficient-frontier](./efficient-frontier/) | 将昂贵前沿模型的判断力用在刀刃上：委托子 Agent 处理高 token 消耗任务，保留主 Agent 做架构规划与最终审查 | - |
| [skillevolver](./skillevolver/) | 面向在线技能学习的元技能自演化框架 | v2.0 |
| [skill-adaptor](./skill-adaptor/) | 基于轨迹的LLM智能体自适应技能，显式故障归因 | - |
| [factorengine](./factorengine/) | 程序级知识注入因子挖掘框架 | v2.0 |
| [agentic-factor-investing](./agentic-factor-investing/) | AI 自主因子发现与系统化投资框架 | v2.0 |
| [embodiskill](./embodiskill/) | 面向具身技能自演化的技能感知反思与进化 | v2.0 |

### 📐 量化策略
| Skill | 说明 |
|-------|------|
| [multi-factor-scoring](./multi-factor-scoring/) | 多因子量化交易系统，支持因子打分、回测和模拟 |

## 统计

- 总数：**19** 个自建 Skill
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
