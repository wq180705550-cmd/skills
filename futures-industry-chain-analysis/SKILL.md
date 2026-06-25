---
name: futures-industry-chain-analysis
description: |
  商品期货产业链自动化分析系统 v2.9（自下而上+置信度优先+信号筛选）。
  触发词：商品期货分析、产业链分析、期货交易建议、期货策略、大宗商品分析
  数据源：交易所官方API（exchange-futures-data skill，最高优先级）→ TqSdk（实时行情）→ AKShare（futures_main_sina，降级）
  覆盖：12大产业链、67+活跃品种（OI>10000）
  核心逻辑：自下而上（品种信号→产业链验证→置信度排序），置信度优先（胜率>赔率）
version: "2.9.1"
changelog: |
  v2.9.1 (2026-06-24): 筛选逻辑修复（置信度阈值+市场环境过滤）
    - 修复：移除绕过置信度阈值的逻辑，严格执行40%下限
    - 修复：辩论结果HOLD不再视为"一致"，改为中性降权（×0.85）
    - 新增：市场环境惩罚，偏空市场多头信号额外惩罚20%
    - 新增：动态共振度阈值，偏空市场做多需60%共振度
    - 新增：test_screen.py 市场环境过滤测试（11个测试100%通过）
  v2.9.0 (2026-06-24): 自下而上逻辑重构+信号筛选模块
    - 新增：screen.py 信号筛选模块（趋势阶段检测+多指标共振度+产业链验证）
    - 重构：run_pipeline.py 为7阶段自下而上管道
    - 重构：debate.py 为信号级辩论（非产业链级）
    - 重构：report.py 为置信度优先排序展示
    - 修复：AKShare数据源从futures_zh_spot()切换到futures_main_sina()
    - 扩展：67个品种（OI>10000），含碳酸锂/工业硅/集运指数等新品种
  v2.8.0 (2026-06-22): SKILL.md重构+模块化+测试100%
    - 拆分：内联代码→scripts/模块（config/chains/indicators/debate/trade_plan/risk/report/data_fallback/run_pipeline）
    - 测试：155个单元测试，100%通过
    - 数据降级：新增通达信MCP（tdx-connector）作为TqSdk之后的第二降级源
    - 品种名称：op = 双胶纸（郑商所），纸浆造纸链下游产品
  v2.7.0 (2026-06-22): 自下而上+置信度优先重构
agent_created: true
---

# 商品期货产业链自动化分析

## ⚠️ 关键警告

1. **高持仓 ≠ 趋势向上**：持仓量只代表市场关注度，不代表趋势方向
2. **趋势判断必须基于技术指标**：使用主力连续合约（`KQ.m@EXCHANGE.product`）获取K线
3. **禁止模拟数据**：所有价格必须来自TqSdk实时查询，缺失标注"数据缺失"

---

### 第零原则：右侧交易铁律（全局强制，高于所有其他规则）

**所有交易方案生成必须基于已确认的右侧价格行为信号，禁止左侧猜测。**

1. **得分/置信度 ≠ 交易信号**：趋势评分（-100~+100）、置信度得分（0~1.0）、共振度（0~1.0）等量化指标**只描述当前市场状态**，不是入场信号。高分≠立刻做多，低分≠立刻做空。
2. **强趋势中指标会"钝化"**：在强空头趋势中，RSI可以连续数周<30；在强多头趋势中，RSI可以连续数周>70。ADX>25确认强趋势时，趋势延续概率远大于反转。
3. **趋势阶段检测不是右侧信号**：`detect_trend_stage()`输出的"初期/中期/末期"是技术状态描述，不是入场确认信号。必须等待价格行为确认后才能转化为交易建议。
4. **必须等待右侧确认**：
   - MA排列确认：价格已站上/跌破MA20且MA20走平或拐头
   - MACD确认：底背离/顶背离在至少2根K线后被确认
   - K线形态确认：反转形态（锤子线/吞没等）被下一根K线验证
   - DMI确认：+DI和-DI在ADX>25背景下完成有效交叉
   - 量价确认：放量+持仓增加验证突破有效性
5. **无信号则HOLD（强制）**：没有任何右侧信号被确认时，交易方案必须为HOLD（观望）。禁止用"轻仓试多/试空"替代观望。
6. **置信度过滤仍需右侧确认**：即使置信度≥0.4，若无右侧信号确认，方案自动降级为HOLD。

## 架构概览

```
scripts/
├── config.py          # 配置管理：系统参数、权重、阈值、辩论权重
├── chains.py          # 产业链定义：12链映射、聚类、龙头选择
├── indicators.py      # 技术指标：MA/MACD/RSI/DMI/ATR/OBV + 趋势评分
├── screen.py          # 信号筛选：趋势阶段检测+多指标共振度+产业链验证
├── debate.py          # 多空辩论：信号级辩论（非产业链级）+ 研究主管裁决
├── trade_plan.py      # 交易方案：置信度×0.7 + 盈亏比×0.3 综合排序
├── risk.py            # 风险评估：三方辩论（激进/保守/中性）+ 风险主管裁决
├── report.py          # 报告生成：置信度优先排序 + 产业链概览（Markdown + HTML）
├── data_fallback.py   # 数据降级：TqSdk→AKShare→通达信→Cache
└── run_pipeline.py    # 主入口：7阶段自下而上管道
tests/
├── test_config.py     # 配置测试（33个）
├── test_chains.py     # 产业链测试（25个）
├── test_indicators.py # 指标测试（12个）
├── test_screen.py     # 信号筛选测试（新增）
├── test_debate.py     # 辩论测试（17个）
├── test_trade_plan.py # 交易方案测试（21个）
├── test_risk.py       # 风险测试（14个）
├── test_report.py     # 报告测试（10个）
├── test_data_fallback.py # 降级测试（7个）
└── test_pipeline.py   # 流程测试（2个）
```

## 执行流程（自下而上+置信度优先）

```
Phase 1 数据采集
  TqSdk/AKShare获取K线 → 技术指标计算 → 趋势评分（-100~+100）
      ↓
Phase 2 产业链聚类（验证参考）
  12产业链分类 → 平均得分 → 整体趋势 → 龙头选择
  仅作为信号验证参考，不直接决定交易方向
      ↓
Phase 3 信号筛选（自下而上核心）
  67个品种逐一扫描 → 趋势阶段检测 → 多指标共振度检查
  筛选条件：
    - |得分| ≥ 20
    - 共振度 ≥ 50%（6指标中至少3个同向）
    - 趋势阶段 ≠ 末期（exhausted）
      ↓
Phase 4 信号级辩论+置信度计算
  对每个候选信号进行多空辩论（非产业链级）
  置信度 = 信号强度50% + 多指标共振25% + 产业链验证25%
  产业链验证：同向+15% | 背离-10% | 同链60%+同向+5%
  置信度 < 0.4 → 自动HOLD
      ↓
Phase 5 交易方案生成（置信度优先排序）
  推荐分 = 置信度×0.7 + 盈亏比标准化×0.3
  按置信度降序排列，盈亏比作为次要排序
  目标价 = max(波动率分档目标, 最近关键技术位)
  止损价 = 基于ATR×2.0动态计算
      ↓
Phase 6 风险评估
  激进/保守/中性三方辩论 → 风险主管裁决
  评分≥6→维持 | 4-6→减半 | <4→取消
      ↓
Phase 7 生成报告
  机会汇总表（按置信度排序）+ 产业链概览（验证参考）
  Markdown + HTML（Chart.js交互图表）
  → F:\Commodities\Reports\industry-chain\
  → **报告中必须标注**：报告生成时间 + 数据获取时间（格式"截至 YYYY-MM-DD HH:MM"）
  → **数据时效性**：每条关键数据旁标注截取时间戳
```

## 设计原则

### 自下而上分析逻辑
1. **品种信号优先**：先扫描每个品种的技术信号，发现趋势初期的品种
2. **产业链验证**：用产业链整体趋势验证品种信号的可靠性
3. **置信度排序**：按置信度降序排列，宁缺毋滥

### 置信度优先（胜率>赔率）
1. **首要目标**：保证高胜率（置信度≥40%）
2. **次要目标**：保证高盈亏比（≥1.0:1）
3. **理想状态**：推荐的操作建议都是高置信度高盈亏比的交易机会

### 趋势阶段检测
- **初期（early）**：MA刚排列，MACD刚金/死叉，RSI 40-60 → 质量×1.2
- **中期（mature）**：趋势已确立，动量充足 → 质量×1.0
- **末期（exhausted）**：RSI>70或<30，价格远离MA20 → 质量×0.5（自动排除）

### 多指标共振度
6个指标检查方向一致性（至少3个同向才通过）：
1. MA排列（MA5>MA10>MA20 或 MA5<MA10<MA20）
2. MACD DIF方向
3. RSI趋势（>50多头，<50空头）
4. DMI（+DI>-DI多头，+DI<-DI空头）
5. OBV vs MA20
6. 价格 vs MA20

## 产业链定义

| 产业链 | 品种 | 辩论焦点 |
|--------|------|----------|
| 黑色系 | i,j,jm,rb,hc,SF,SM | 成本推涨vs需求拉动 |
| 能源链 | sc,lu,fu,bu,pg,ec | 裂解价差+集运指数 |
| 聚酯链 | PX,TA,PF,PR | 聚酯利润 |
| 油化工 | eg,eb,v,pp,l,PL,ps,bz | 烯烃利润+新品种聚焦 |
| 煤化工 | MA,SH | MTO/MTP价差 |
| 有色 | cu,al,zn,pb,ni,sn,ao,si,SS,ad,lc | 铝产业链+镍产业链+碳酸锂+工业硅 |
| 贵金属 | au,ag,pt | 黄金-白银比价 |
| 油脂油料 | a,b,m,y,p,OI,RM,PK | 压榨利润 |
| 谷物软商品 | c,cs,SR,CF,CY,jd,lh,AP,CJ,rr | 农产品周期 |
| 建材 | FG,SA,UR | 纯碱→玻璃 |
| 橡胶 | ru,nr,br | 天然vs合成 |
| 纸浆造纸 | sp,op（双胶纸） | 纸浆-双胶纸价差 |

## 数据源优先级

```
交易所官方API（最权威，无爬虫合规风险）
  ↓ 失败
TqSdk（实时行情，首选）
  ↓ 失败
AKShare（futures_main_sina，降级首选）
  ↓ 失败
Cache（历史缓存）
```

**交易所官方API支持**：
- **大商所 (DCE)**：日周月行情、合约参数、仓单、持仓统计
- **上期所 (SHFE)**：JSON格式日线数据，包含成交额
- **郑商所 (CZCE)**：HTML格式日线数据，2015年11月11日前后接口切换
- **中金所 (CFFEX)**：股指期货、国债期货日线数据
- **广期所 (GFEX)**：碳酸锂、工业硅期货数据

**数据格式**：
- DCE：TSV格式，需要解析不规则tab分隔
- SHFE：JSON格式，数据结构清晰
- CZCE：HTML格式，需要HTMLParser解析
- CFFEX：CSV格式
- GFEX：JSON格式

**注意**：
- 交易所官方数据最权威，无爬虫合规风险
- 仅支持日频数据，无实时Tick
- 各交易所有调用频率限制，建议间隔1秒以上
- AKShare使用 `ak.futures_main_sina(symbol, start_date, end_date)` 获取K线
- CZCE品种（SF/SM/MA等）需转小写（sf/sm/ma）才能被AKShare识别
- 通达信MCP支持期货日线数据，可作为辅助数据源

## 使用方式

```python
# 方式1：运行完整流程（推荐）
from scripts.run_pipeline import run_pipeline
result = run_pipeline(
    output_dir='F:/Commodities/Reports/industry-chain',
    data_dir='F:/Commodities/Temp'
)

# 方式2：按需加载单个模块
from scripts.config import CONFIG_MANAGER, get_adaptive_weights
from scripts.chains import cluster_chains, CHAIN_PRODUCTS
from scripts.indicators import calculate_trend_score, compute_indicators
from scripts.screen import screen_signals, detect_trend_stage, count_resonance
from scripts.debate import bull_argument, bear_argument, research_manager_decision
from scripts.trade_plan import generate_trade_plan, calc_confidence
from scripts.risk import aggressive_risk_assessment, risk_manager_decision
from scripts.report import generate_markdown_report, generate_html_report

# 方式3：信号筛选（自下而上核心）
from scripts.screen import screen_signals
candidates = screen_signals(
    symbols=['rb', 'hc', 'i', 'j', 'jm', 'SF', 'SM'],  # 品种列表
    score_threshold=20,      # 得分阈值
    min_resonance=0.5,       # 最小共振度
    exclude_exhausted=True   # 排除末期趋势
)
# 返回：[{'symbol': 'rb', 'score': -94, 'stage': 'mature', 'resonance': 0.83, ...}, ...]
```

## 运行测试

```bash
cd futures-industry-chain-analysis
python -m unittest discover -s tests -v
```

## 硬规则

1. **数据真实性**：所有价格必须来自TqSdk/AKShare实时查询
2. **趋势判断基于指标**：必须使用技术指标判断趋势，禁止仅凭持仓量推测
3. **主力连续合约**：获取K线必须使用`KQ.m@EXCHANGE.product`格式（TqSdk）或主力合约代码（AKShare）
4. **止损合理性**：止损价必须基于ATR×2.0动态计算
5. **风险收益比**：目标收益/止损损失 ≥ 1.0
6. **置信度过滤**：置信度 < 0.4 自动降级为HOLD
7. **产业链逻辑**：交易建议必须有产业链逻辑支撑
8. **信号筛选**：必须先扫描所有品种信号，再进行产业链验证
9. **置信度优先**：排序时置信度权重70%，盈亏比权重30%
10. **宁缺毋滥**：宁可不推荐，也不推荐低置信度机会
