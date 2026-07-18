# CFA Level 3 深度学习知识库（Curriculum Knowledge Base）

> 本文件是 `cfa-l3-mastery` 技能的核心知识库，编码 CFA Level 3 课程体系的学科知识与应试要点。
> 配套文件：`l3_materials.md`（网盘资料按主题+最近年份映射）、`assets/cfa_l3_inventory.csv`（完整 L3 清单）。
> 知识以 **2024 L3 课程（V1–V5）** 为最新完整基准；道德部分以 **2025/2026 考纲** 为最新。

---

## 一、L3 考试结构与应试哲学

CFA L3 与 L1/L2 的本质区别：从"选择正确答案"转向"**构建并论证答案**"。

- **考试形式（机考 CBT）**：两级均含 **论述题（Constructed Response / Essay）** 与 **选择题（Item Set）**。论述题要求用文字+计算展示推理过程，而非选字母。
- **题量结构**：每级约 8–11 个 vignette（案例），其中论述题占约 50% 权重。论述题常要求：给出投资建议、计算最优配置、撰写 IPS 段落、解释风险管理选择。
- **评分特点**：论述题按"关键点（rubric）"给分，未展示过程/未答到关键词即丢分；计算题步骤分重要。
- **时间管理**：论述题每题约 10–15 分钟，先读问题（command words）再读案例；遇到卡点先跳，保证覆盖所有题。
- **Command words（指令词）识别**：
  - *Calculate / Compute* → 必须给出数值与单位。
  - *Determine / Identify* → 给出结论即可，但需依据。
  - *Justify / Explain / Discuss* → 必须用文字陈述理由，至少 2–3 句逻辑链。
  - *Recommend* → 先给结论，再给支撑。
  - *Contrast / Compare* → 分点对照两者差异。

### L3 答题黄金法则
1. **先答 command word，再展开**。阅卷先找关键词。
2. **计算展示全过程**：列公式→代入→结果，哪怕用数值估算也展示。
3. **IPS 类题结构化**：先写约束（ liquidity / time / tax / legal / unique ），再给配置建议。
4. **不空题**：论述题写方向性文字也有部分分。

---

## 二、主题领域与权重（2024 L3）

L3 以 **投资组合管理（Portfolio Management）** 为核心，权重最高（约 35–40% 总权重），其余为单资产类别的"组合管理视角"应用。

| 主题领域 | L3 重点 | 近似权重 |
|---|---|---|
| Portfolio Management（核心） | 资产配置、IPS、行为金融、CME、风险管理、执行、绩效 | ~35–40% |
| Economics | 宏观经济分析、汇率与货币管理 | ~10–15% |
| Equity Investments | 主动权益管理、组合构建 | ~10–15% |
| Fixed Income | 固收组合管理、久期/关键利率、信用 | ~10–15% |
| Derivatives | 衍生品在组合管理中的应用 | ~5–10% |
| Alternative Investments | 另类（PE/RE/基建/对冲基金/商品）的 PM 视角 | ~5–10% |
| Ethics & GIPS | 道德、GIPS、软美元、ROA | ~10% |

---

## 三、核心模块深度学习

### 3.1 资产配置（Asset Allocation, AA）
- **战略资产配置（SAA）**：基于长期资本市场预期（CME）与 IPS 约束，确定政策组合。方法：均值-方差优化、Black-Litterman、基于负债的配置。
- **战术资产配置（TAA）**：在 SAA 偏离带内，利用短期估值/动量机会主动调整；需明确再平衡触发（阈值 vs 日历）。
- **基于负债的管理（ALM）**：适用于机构。两种目标函数：
  - **盈余最大化（Surplus Optimization）**：max E(R_surplus) − 0.5λ·Var(R_surplus)，surplus = 资产 − 负债。
  - **缺口最小化 / 风险预算**：控制盈余波动。
- **风险预算（Risk Budgeting）**：将组合风险（而非资金）分配给子策略；用边际贡献风险（MCR）与成分风险（CR）分配。
- **关键判断**：当资产与负债久期不匹配时，surplus duration 决定利率风险暴露。

### 3.2 资本市场预期（Capital Market Expectations, CME）
- 目标：生成各资产的预期收益、波动、相关性，输入 AA。
- **方法**：历史估计、DDM（股权）、自下而上（盈利+股息）、调查、计量模型。
- **宏观框架**：
  - 增长：产出缺口、产能利用率、人口/生产率。
  - 通胀：菲利普斯曲线、通胀预期、油价冲击。
  - 政策：Taylor Rule：r = r* + π + 0.5(π−π*) + 0.5(y−y*)。
  - 汇率：利率平价、购买力平价、carry。
- **Regime / 周期定位**：扩张/衰退/复苏/滞胀下，资产表现排序不同，需动态调整 CME。
- **偏差来源**：幸存者偏差、平滑收益（如 PE/房地产 appraisal smoothing）、结构性断点。

### 3.3 汇率与货币管理（Currency Management）
- **货币敞口来源**：直接（海外资产本币）、间接（经营现金流）。
- **三种立场**：
  - *Passive*：完全对冲至本币，消除波动。
  - *Active*：基于观点主动管理。
  - *Mismatch/Over-/Under-hedge*。
- **工具**：远期、期货、掉期、期权（参与率/ collar）。
- **策略框架（CME 视角）**：
  - **Carry**：高息货币多仓，低息空仓；风险在于汇率反转。
  - **Volatility**：期权对冲尾部。
  - **Cross-hedging**：用高度相关货币对冲不可对冲货币。
- **关键指标**：hedge ratio、forward points、covered interest parity 偏离。

### 3.4 固定收益组合管理（Fixed-Income PM）
- **收益率曲线管理**：子弹/杠铃/阶梯（bullet / barbell / ladder）的期限敞口取舍。
- **久期管理**：组合久期目标设定；关键利率久期（key-rate duration）刻画非平行移动风险。
- **凸性**：高阶调整，负凸性资产（MBS callable）在利率下行时表现差。
- **信用与利差**：spread duration、credit migration、违约损失（LGD）。
- **结构化产品**：MBS/ABS 的 prepayment 风险、PSA、OAS。
- **衍生品叠加（Derivatives Overlay）**：用期货/互换调整久期而不动现券（cheap to deliver / 税务/流动性考量）。

### 3.5 权益组合管理（Equity PM）
- **主动管理分类**：
  - *Fundamental active*：自下而上基本面（value/growth/quality）。
  - *Quantitative*：因子模型（size/value/momentum/quality/low vol）。
  - *Active share* 高 = 偏离基准多，需有把握的 alpha 来源。
- **智能贝塔（Smart Beta）**：透明、规则化因子暴露；注意因子拥挤与再平衡拖累。
- **组合构建**：约束（行业/个股上限、ESG、税务）、优化（风险模型）、交易成本。
- **ESG 整合**：剔除、倾斜、参与；对预期收益与风险的影响需论证。

### 3.6 衍生品组合管理（Derivatives in PM）
- **远期/期货**：无套利定价 F = S·e^{(r−q)T}；用于 equity index / currency / commodity 暴露调整。
- **互换**：利率互换改融资结构；权益互换获暴露；总收益互换（TRS）。
- **期权**：
  - 支付结构：call/put、bull/bear spread、collar、straddle。
  - 在 PM 中：保护性 put（组合保险）、covered call（增益）、实现特定 payoff 轮廓。
  - 希腊字母：Delta/Gamma/Vega/Theta 用于风险监控。
- **应用判断**：比较"直接交易标的" vs "衍生品复制"的成本、杠杆、流动性。

### 3.7 另类投资（Alternatives, PM 视角）
- **私募股权（PE）**：VC/BUYOUT；J-curve、基金结构（GP/LP、carry）、估值（DCF/可比/最近交易）。
- **房地产**：直接 vs 间接（REIT）；NOI、cap rate、appraisal smoothing。
- **基础设施**：监管回报、长周期、通胀对冲属性。
- **对冲基金**：策略（LS equity / macro / CTA / event-driven / relative value）；fee（1.5/20+）、lock-up、liquidity；尽职调查重点。
- **商品**：滚动收益（roll yield）、contango/backwardation、通胀对冲。
- **L3 重点**：另类在组合中的角色（分散、低相关、流动性溢价）、尽职调查、估值挑战。

### 3.8 风险管理（Risk Management）
- **市场风险**：VaR（历史/参数/蒙特卡洛）、expected shortfall、压力测试、情景分析。
- **线性/非线性**：期权使组合 gamma 暴露，需 delta 对冲或接受凸性。
- **资产负债风险**：利率、通胀、流动性对负债的影响；ALM 缺口。
- **尾部风险**：期权、尾部对冲、相关性在危机中趋 1（diversification breakdown）。
- **风险管理流程**：识别→度量→限额→监控→报告。

### 3.9 交易执行（Execution）
- **实施缺口（Implementation Shortfall）**：决策价 vs 实际成交价的全成本（佣金、价差、行情冲击、机会成本）。
- **调度算法**：VWAP / TWAP / POV / 提前/延迟调度，依流动性与 urgency 选择。
- **市场微观结构**：价差、深度、冲击成本；大单拆分降低冲击但增时间风险。
- **算法选择权衡**： urgency 高→快成交但冲击大；低→冲击小但时间/信息风险大。

### 3.10 绩效评估（Performance Evaluation）
- **GIPS**： composites 构建、外部验证、合规披露（广告合规）。
- **收益度量的坑**：时间加权（TWR，剔除现金流影响）vs 金额加权（MWR）；外部现金流处理（modified Dietz）。
- **归因（Attribution）**：Brinson 模型（配置 + 选择 + 交互）；固定收益归因（duration/timing/sector/curve）。
- **风险调整指标**：Sharpe、Sortino、信息比率（IR = active return / tracking error）、Treynor。
- **基准选择**：反映 mandate、可投资性、明确性、可测性。

### 3.11 IPS：私人财富（Private Wealth IPS）
- **约束**：流动性、时间 horizon、税务（capital gains、estate、income）、法律、独特（ESG/信仰）。
- **税务优化**：asset location（税高效资产放应税账户、税低效放 tax-advantaged）、harvesting losses、持有期。
- **行为偏差应用**：识别客户认知/情绪偏差，调整沟通与配置建议。
- **财富转移**：遗产规划、信托、慈善。

### 3.12 IPS：机构（Institutional IPS）
| 机构类型 | 负债特征 | 配置倾向 |
|---|---|---|
| 养老 DB | 长期、利率敏感、通胀敏感 | 久期匹配负债、信用、少量权益 |
| 基金会 | 永久、支出率约束（通常 ~5%） | 多元、权益权重高、通胀保护 |
| 捐赠金 | 类似基金会、长期 | 另类权重高（流动性容忍） |
| 保险公司 | 短/长负债、监管 | 固收为主、匹配久期、流动性储备 |
| 银行 | 短期、流动性强 | 高流动、低久期 |

### 3.13 行为金融（Behavioral Finance）
- **认知偏差（Cognitive）**：confirmation、anchoring、mental accounting、framing、availability、hindsight、recency。
- **情绪偏差（Emotional）**：loss aversion、overconfidence、herding、regret aversion、endowment。
- **应用**：解释市场异常（泡沫/崩盘）、客户非理性配置、设计 nudges（自动再平衡、目标日期）。
- **与有效市场的关系**：行为偏差 → 有限套利 → 部分可捕获的 anomaly，但需交易成本与容量约束。

### 3.14 道德与 GIPS（L3 重点）
- **GIPS**： composite 必须包含所有付费账户；no survivorship/selection bias；外部验证（recommended）；广告合规（claim 需 substantiated）。
- **软美元（Soft Dollar）**：仅可用于研究服务，须 benefit client；brokerage 安排须 best execution。
- **责任权衡（ROA）**：client > employer > own；conflict 披露。
- **审慎（Prudence）**：现代组合理论视角，按 mandate 分散。
- **业绩宣传**：合规、可验证、含 disclaimer。

---

## 四、L3 复习与答题工作流（技能执行指南）

当用户提出 L3 相关问题（概念、计算、IPS、论述题草稿、资料定位）时：

1. **定位主题**：将问题映射到上述 3.1–3.14 模块。
2. **检索知识**：优先从本文件获取权威概念与公式；确保使用**最新考纲**表述。
3. **映射资料**：调用 `l3_materials.md`，给出网盘中**最近年份**对应的讲义/框架图/视频路径，引导用户打开。
4. **组织答案**：
   - 概念题：定义 → 机制 → 与其他模块联系 → 举例。
   - 计算题：列公式 → 代入 → 结果 → 经济含义。
   - IPS 题：约束清单 → 目标 → 配置建议 → 理由（结合行为/税务）。
   - 论述题：先 command word，再分点（每点含结论+理由），展示计算。
5. **去重叠提醒**：若用户引用旧年份资料，提示"以最近年份版本为准"（见 `l3_materials.md` 的 ★ 推荐项）。

---

## 五、与其他级别资料的衔接

- 网盘同时含 L1/L2 资料（见 `assets/cfa_inventory.csv`）。L3 建立在 L1/L2 基础之上：
  - L1 打底（工具、伦理、基础概念）；
  - L2 深化（估值、财报、量化）；
  - L3 聚焦"组合管理 + 论证表达"。
- 当用户问跨级别问题，先判定级别，再调用对应知识；L3 资料以 2024/2025 考纲为最新。
