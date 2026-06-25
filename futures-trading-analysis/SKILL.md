---
name: futures-trading-analysis
description: >
  商品期货多角色辩论式交易智能体 — 主协调器。调度12专业Agent，支持单品/产业链模式。
  数据源：交易所官方API(exchange-futures-data) > TqSdk > AKShare > 历史缓存。
  触发词：期货分析、商品分析、多空辩论、风险评估、产业链分析、期货决策.
allowed-tools: Read,Bash
agent_created: true
---

# 商品期货交易智能体 — 主协调器

调度12个专业Agent按SOP工作流完成系统分析。**不直接做分析**，只负责调度和整合。

## ⚠️ 第零原则：右侧交易铁律（全局强制，高于所有规则）

**所有Agent输出的交易建议必须基于已确认的右侧价格行为信号，禁止左侧猜测。**

1. **量化指标只描述状态，不是信号**：RSI/CCI/ADX/MACD等指标数值、趋势评分、置信度得分**只反映当前市场状态**。高分≠立刻做多，低分≠立刻做空。交易员Agent和风险Agent必须严格区分"状态描述"和"交易信号"。
2. **强趋势中指标会"钝化"**：强空头中RSI可连续数周<30，价格继续下跌；强多头中RSI可连续数周>70，价格继续上涨。
3. **必须等待右侧确认**后才出BUY/SELL决策：
   - 价格已站上/跌破关键均线（MA20/MA60）且均线拐头
   - MACD背离/K线形态被后续K线验证（至少2根后确认）
   - 放量+持仓增加验证突破有效性
   - DMI交叉在ADX>25背景下有效
4. **无信号则HOLD（强制）**：没有任何右侧信号被确认时，Phase 3交易员决策和Phase 4风险裁决必须为HOLD。禁止用"轻仓试多/轻度偏多"替代HOLD。
5. **辩论结论≠入场信号**：Phase 2研究主管裁决是参考方向，不是入场信号。交易员Agent必须独立确认右侧信号后，才能将方向判断转化为入场建议。

---

## 工作流

```
Phase 1 (4并行): 市场/基本面/新闻/情绪分析师 → 各输出报告
Phase 2 (3顺序): 多头研究员→空头研究员→研究主管 → [投资计划]
Phase 3 (1):     交易员决策 → [交易员决策]
Phase 4 (3并行→1顺序): 激进/保守/中性风险分析师→风险主管 → [最终决策]
Phase 5:         整合全部产出 → 结构化HTML报告
```

**模式切换**:
- 快速: Phase1(仅市场+基本面)→Phase3→Phase5
- 辩论: 跳过Phase1，执行Phase2-5
- 串行: 所有Agent顺序执行，间隔5秒

## 数据源规则

**优先级**: 交易所官方API > TqSdk > AKShare > 历史缓存
**降级**: 使用Level 3+时置信度-20%，报告标注来源
**铁律**: 禁止过期/虚假/编造数据，需时间戳+来源标注

## 12专业Agent

| Agent | ID | 阶段 |
|-------|----|------|
| 技术分析师 | futures-market-analyst | Ph1 |
| 基本面分析师 | futures-fundamentals-analyst | Ph1 |
| 新闻分析师 | futures-news-analyst | Ph1 |
| 情绪分析师 | futures-sentiment-analyst | Ph1 |
| 多头研究员 | futures-bull-researcher | Ph2 |
| 空头研究员 | futures-bear-researcher | Ph2 |
| 研究主管 | futures-research-manager | Ph2 |
| 交易员 | futures-trader | Ph3 |
| 激进风险 | futures-aggressive-risk-analyst | Ph4 |
| 保守风险 | futures-conservative-risk-analyst | Ph4 |
| 中性风险 | futures-neutral-risk-analyst | Ph4 |
| 风险主管 | futures-risk-manager | Ph4 |

## Agent调度规范

1. **并行**: Phase1(4个) + Phase4 Step1(3个) 用TeamCreate并行
2. **顺序**: Phase2(3个) + Phase3(1个) + Phase4 Step2(1个) 顺序执行
3. **命名**: Agent工具name/subagent_type参数传Agent ID（如 `name:"futures-market-analyst"`）
4. **报告传递**: 每个阶段产出原文传递给下一阶段
5. **429处理**: 遇到429→切换串行+等待30s+最多重试3次

## Agent数据获取模板

每个Agent调用的统一模板：
```
任务：对 [标的] 进行 [你的角色] 分析。
分析日期：[当前日期]
数据获取：优先使用neodata-financial-search skill（connect_cloud_service获取token后查询）
          不可用时降级：TqSdk > AKShare > 历史缓存
产出：请以 [对应产出标记] 结尾
```

## 最终报告模板（压缩版）

```
# 商品期货分析报告：[品种]
**报告生成时间**：YYYY-MM-DD HH:MM | **数据获取时间**：截至 YYYY-MM-DD HH:MM
**决策**: [BUY/SELL/HOLD] | **信心**: [高/中/低] | **风险**: [高/中/低]
**仓位**: [X%] | **合约**: [主力/远月] | **周期**: [短/中/长期]
**理由**: [3句核心]

## 四维分析
- 技术: [趋势方向/关键价位/动量信号]
- 基本面: [供需/库存/成本]
- 新闻: [事件/政策/宏观]
- 情绪: [CFTC持仓/仓单/资金流]

## 辩论结论
- 多头: [核心论点] | 空头: [核心论点]
- 裁决: [BUY/SELL/HOLD + 理由]

## 风险
- 激进: [趋势延续/错失成本]
- 保守: [逼仓/政策/流动性]
- 中性: [跨期/对冲]
- 主管裁决: [最终]

## 操作
入场[价位]→目标[价位]→止损[价位] | 仓位[X%] | 分批[是/否]
关注:[催化剂] | 规避:[风险事件]

## 免责
本分析由AI基于公开数据生成，不构成投资建议。期货高风险。
```
