---
name: multi-factor-scoring
description: "Multi-factor scoring quantitative trading system. Build quantitative trading strategies from multi-factor scoring (momentum, technical, volume, fundamentals, macro, sector rotation) across A-shares, HK stocks, US stocks, and futures/derivatives on daily/4H/1H/15M timeframes. Includes a 4-layer scoring framework (sprout/volume-price/structure/confirmation) with veto rules, a realized-volatility forecasting module (Log-HAR + TTM ensemble), a distribution-free uncertainty-quantification module (dependence-aware bootstrap + conformal intervals), and an FTS factor-governance module (3-level evaluation chain, walk-forward validation, decay test, circuit breaker, orthogonalization, atomic persistence), and a deployment-discipline layer (effective-sample-size gate, shadow-before-swap forward-gated model replacement, interval coherence projection, passive market-impact costing, herding/crowding read), and an uncertainty-to-sizing & robust-structure layer (conformal-Kelly interval-width position sizing, exposure-similarity factor-graph structure, non-Gaussian long-memory drawdown budgeting, certified Wasserstein distributionally-robust allocation, forecast-gap Shapley attribution, sentiment classification-vs-return-predictability guard, sector-embedding cross-sectional heterogeneity), and a production-feedback & scope-boundary layer (auto-recalibration trigger, online-learning guard, real-time cost calibration, ML-portfolio scope boundary, alternative-data admission), and a this-week arXiv integration layer (regime-gated MoE volatility routing, calibration-period-aware quantization deployment gate, disentangled alpha/beta trigger signals with epistemic covariance shrinkage, specification-satisfaction backtest verification, inter-sectoral signed-network imbalance monitor, lower-spectrum synchronization factor, FOMC pre-announcement volatility gate, classification-boundary proximity monitor). Triggers: multi-factor models, scoring systems, factor-based stock selection, rotation strategies, quantitative trading framework, 4-layer scoring, volatility forecasting/HAR, uncertainty quantification/conformal prediction, position confidence, risk thresholds, factor governance/admission gates, model promotion policy, backtest audit, conformal-Kelly sizing, distributionally-robust portfolio optimization, drawdown budgeting, forecast attribution."

agent_created: true
version: 2.9.0
language: zh
type: strategy
priority: high
triggers:
  - "多因子评分系统"
  - "4层评分框架/萌芽-量价-结构-确认"
  - "因子选股/量化策略"
  - "multi-factor scoring"
  - "OI变化率/ATR/OBV/CMF"
  - "否决项/ADX/RSI极端"
  - "波动率预测/HAR/Log-HAR/TTM"
  - "realized volatility / TSFM ensemble"
  - "不确定性量化/置信区间/共形预测"
  - "仓位置信度/风控阀值/自助法"
  - "uncertainty quantification / conformal prediction / bootstrap CI"
  - "成本感知配置/RL组合优化/SciPhyRL/多期配置"
  - "基率诚实/方向准确率/TimesFM显著性/方向性信号"
  - "去噪相关/市场广度/板块协同/相关性网络"
  - "特征向量旋转/危机领先指标/TVP-Kalman/临界转变"
  - "厚尾风险/CVaR/尾部风险闸门/时变采样"
  - "新闻情绪/另类数据因子/transformer情绪"
  - "趋势跟随理论/谱质量/成本最优回看窗口"
  - "三闸门准入/信号审计/回测取证/purged split"
  - "校准评分/Brier/Winkler/过度自信缩仓"
  - "TDA拓扑聚类/保留机制/换手控制"
  - "非对称波动/GJR/CVaR配置/Rachev"
  - "特征驱动协方差/CD-DFM/零样本接入新标的"
  - "影子换模/前瞻门控晋升/Shadow Before Swap"
  - "有效样本量/ESS/能力归因/证据不足"
  - "分位数交叉/区间相干性投影/KQSP"
  - "被动市场冲击/限价单成交概率/未成交风险"
  - "羊群效应/CSAD/LSV/拥挤度/动量衰竭反转"
  - "市场对齐情绪RL/FinSMART"
  - "共形Kelly/区间宽度仓位/分数Kelly/Conformal Kelly"
  - "因子暴露图/MINGLE/暴露相似度/图局部性"
  - "回撤预算/最长恢复时间/长记忆回撤/非高斯回撤/fBM"
  - "Wasserstein鲁棒优化/分布鲁棒配置/认证近似LP/DRO"
  - "预测差归因/Shapley归因/CCAR/CECL"
  - "情绪分类vs收益可预测/QLoRA/前瞻IC显著性/Newey-West"
  - "板块嵌入/横截面异质性/短期反转/知情流持续性/龙虎榜席位"
  - "自动重校准/实盘反馈闭环/auto-recalibration trigger"
  - "在线学习护栏/权重热替换/shadow-before-swap 升级"
  - "实时成本监控/冲击成本实证标定/成本回流校准"
  - "ML组合层/学习排序/RL配置/组合器范围边界"
  - "另类数据准入/卫星数据/供应链数据/point-in-time校验"
  - "能力差距矩阵/FTS对标/演进路线"
  - "regime-gated MoE/专家路由波动率/soft routing/波动率集成"
  - "PTQ量化/激活校准/部署期覆盖/4-bit量化部署"
  - "解耦alpha/beta触发/认知不确定性协方差收缩/LLM小盘交易"
  - "目标导向量化投资/规范满足验证/搜索宽度deflation"
  - "有符号相关网络/部门间失衡/结构平衡极化/系统性风险监控"
  - "相关矩阵下谱/市场同步/最小特征值/分散度因子"
  - "FOMC预告/波动率曲面/事件驱动波动闸门"
  - "分类边界邻近/准入不确定性/ST监控状态"
keywords: [multi-factor, quantitative-trading, scoring-system, factor-selection, A-shares, HK-stocks, US-stocks, futures, derivatives, OI, ATR, OBV, CMF, Supertrend, HMA, Donchian, DMI, MACD, realized-volatility, HAR, Log-HAR, TTM, TSFM, ensemble, VOLARE, uncertainty-quantification, conformal-prediction, block-bootstrap, tsbootstrap, confidence-interval, position-confidence, risk-gate, EnbPI, cost-aware-allocation, SciPhyRL, base-rate, directional-significance, correlation-denoising, market-breadth, eigenvector-rotation, early-warning, tail-risk, CVaR, news-sentiment, alternative-data, trend-following, spectral-mass, cost-optimal-span, triple-gate-admission, backtest-audit, purged-split, calibration, Brier-score, Winkler-score, TDA, topological-clustering, retention-mechanism, GJR-GARCH, asymmetric-volatility, Rachev-ratio, CD-DFM, characteristic-covariance, zero-shot-onboarding, critical-slowing-down, event-heterogeneity, shadow-before-swap, forward-gated-promotion, effective-sample-size, skill-attribution, quantile-crossing, KQSP, coherence-projection, passive-market-impact, fill-probability, non-execution-risk, herding, CSAD, LSV, crowding, momentum-exhaustion, market-aligned-RL, FinSMART, conformal-kelly, fractional-kelly, interval-width-sizing, MINGLE, exposure-similarity-graph, factor-graph, drawdown-budget, fractional-brownian, long-memory-drawdown, wasserstein-dro, distributionally-robust, certified-approximation, forecast-gap-attribution, shapley-attribution, CCAR, CECL, sentiment-return-gap, QLoRA, forward-IC, newey-west, sector-embeddings, cross-sectional-heterogeneity, short-term-reversal, informed-flow, LHB-seat-persistence, auto-recalibration, live-feedback-loop, online-learning-guard, hot-weight-replacement, real-time-cost-monitoring, cost-calibration, ml-portfolio-layer, learning-to-rank, rl-allocation, portfolio-scope-boundary, alternative-data-admission, satellite-data, supply-chain-data, point-in-time-validation, capability-gap-matrix, fts-benchmark, regime-gated-moe, volatility-routing, ptq-calibration, quantization-deployment-gate, alpha-beta-trigger, epistemic-covariance-shrinkage, spec-satisfaction-verification, intersectoral-imbalance, signed-network, lower-spectrum-sync, fomc-preannouncement, volatility-gate, classification-boundary-proximity, eligibility-monitor]
config:
  framework: "6-category"  # or "4-layer"
  ashare_data_source: "akshare"
  us_data_source: "yfinance"
---

# Multi-Factor Scoring Quantitative Trading System

## Overview

This skill provides a complete framework for building and deploying a multi-factor scoring quantitative trading system. It evaluates stocks across six factor categories (momentum, technical indicators, volume, fundamentals, macro, sector) with customizable weights, generates buy/sell signals based on dynamic thresholds, and supports backtesting and simulated trading across A-shares, HK stocks, US stocks, and futures/derivatives on multiple timeframes (daily swing, 4H, 1H, 15M).

### Two Built-in Scoring Frameworks

This skill now supports two complementary scoring models. The user can choose one at the start of the task or combine them:

1. **6-Category Framework** (default): momentum / technical indicators / volume / fundamentals / macro / sector. Best for general equity multi-factor stock selection.
2. **4-Layer Framework** (new): sprout / volume-price / structure / confirmation. Best for short- to medium-term trend timing, especially when Open Interest (OI) data is available (futures, options, and some index/ETF contracts).

| Framework | Weight Style | Best For | Required Data |
|-----------|--------------|----------|---------------|
| 6-Category | Cross-sectional factor weights | Long-term equity factor portfolios | Price, volume, fundamentals, macro |
| 4-Layer | Sequential confirmation layers | Trend-sprout timing, futures/derivatives | Price, volume, **OI (optional)** |

When the user references the 4-layer framework, OI indicators, or veto rules (ADX<15, RSI extreme, OI divergence, high fee rate), switch to the 4-Layer Framework implementation. Otherwise, default to the 6-Category Framework.

## Core Capabilities

### 1. Multi-Factor Scoring Engine

To calculate a composite score for each stock, the system evaluates six factor categories:

**Factor Categories and Default Weights:**

| Factor Category | Default Weight | Description |
|----------------|----------------|-------------|
| Momentum | 25% | Price momentum, returns over multiple periods |
| Technical Indicators | 20% | RSI, MACD, Bollinger Bands, moving averages |
| Volume | 15% | Volume change, volume-price divergence |
| Fundamentals | 20% | P/E, P/B, ROE, revenue growth, profit margins |
| Macro Economy | 10% | Interest rates, CPI, PMI, monetary policy |
| Sector/Industry | 10% | Sector rotation, industry trends, relative strength |

**Customizing Weights:**

Users can customize factor weights by modifying the `factor_weights` dictionary in `scoring_engine.py`:

```python
factor_weights = {
    'momentum': 0.25,
    'technical': 0.20,
    'volume': 0.15,
    'fundamental': 0.20,
    'macro': 0.10,
    'sector': 0.10
}
```

Total weights should sum to 1.0.

### 2. Scoring Methodology

**Momentum Factor (25%):**
- 1-month, 3-month, 6-month returns
- Risk-adjusted momentum (return / volatility)
- Relative strength vs. benchmark

**Technical Indicators (20%):**
- RSI (14): Oversold/overbought conditions
- MACD: Trend and momentum
- Bollinger Bands: Volatility and mean reversion
- Moving averages: Trend direction (MA20, MA60, MA200)

**Volume (15%):**
- Volume change vs. 20-day average
- Volume-price divergence (price up, volume down = negative)
- Accumulation/Distribution line

**Fundamentals (20%):**
- Valuation: P/E, P/B, EV/EBITDA
- Profitability: ROE, ROA, profit margin
- Growth: Revenue growth, earnings growth
- Financial health: Debt/Equity, current ratio

**Macro (10%):**
- Interest rate trends
- Inflation (CPI, PPI)
- Economic growth (GDP, PMI)
- Monetary policy stance

**Sector (10%):**
- Sector relative strength vs. market
- Industry rotation signals
- Sector momentum

Each factor is normalized to a 0-100 score, then weighted and summed to produce a composite score.

### 3. 4-Layer Scoring Framework (萌芽 / 量价 / 结构 / 确认)

When the user asks for trend-sprout timing, OI-based filtering, or the specific 4-layer framework shown below, use this model instead of (or in addition to) the 6-category framework.

```
总满分 100 分 = L1 萌芽 55 分 + L2 量价 15 分 + L3 结构 15 分 + L4 确认 15 分
最终得分 = 各层加权得分 − 否决项扣分
```

| 层级 | 权重 | 指标 | 计算要点 | 评分方向 |
|------|------|------|---------|---------|
| **L1 萌芽** | 55% | OI变化率、ATR百分位、OBV趋势、CMF | 趋势早期放量 + 波动扩张 + 资金流确认 | 捕捉趋势萌芽 |
| **L2 量价** | 15% | CCI、Supertrend、HMA方向、量比 | 价格动量 + 趋势方向 + 成交量配合 | 确认量价共振 |
| **L3 结构** | 15% | RSI健康区、DMI(+DI/-DI)、前高突破 | 非极端 RSI + DMI 多头排列 + 价格突破前高 | 结构支撑 |
| **L4 确认** | 15% | Donchian突破、均线排列、MACD金叉 | 多周期均线顺向 + 通道突破 + 动量金叉 | 最终入场确认 |

#### L1 萌芽 (55%) — 早期趋势识别

1. **OI 变化率** (15%): 期货/期权市场使用。
   - 计算: `(OI_t − OI_t-5) / OI_t-5 × 100%`
   - 加分: OI 增长率 > 5%（资金流入）
   - 扣分: OI 增长率 < −5%（资金流出）
   - 无 OI 数据的股票场景: 用成交量 5 日增长率替代

2. **ATR 百分位** (15%): 衡量波动率处于近期什么位置。
   - 计算: 当前 ATR(14) 在过去 60 天 ATR 中的百分位
   - 加分: ATR 百分位 > 60%（波动扩张，突破在即）
   - 扣分: ATR 百分位 < 20%（盘整，无方向）

3. **OBV 趋势** (15%): 量价累积趋势。
   - 计算: OBV 斜率（线性回归 10 日）
   - 加分: OBV 斜率 > 0 且价格同步新高
   - 扣分: OBV 斜率 < 0 或价格与 OBV 顶背离

4. **CMF (Chaikin Money Flow)** (10%): 资金流向。
   - 计算: CMF(20) = 累计(ADL) / 累计(Volume)
   - 加分: CMF > 0.05
   - 扣分: CMF < −0.05

#### L2 量价 (15%) — 量价共振

1. **CCI** (4%): 商品通道指数。
   - 加分: CCI(14) 在 +100 上方（强势）或从 −100 下方回升（超卖反弹）
   - 扣分: CCI 在 +200 以上（超买）或 −200 以下（极度弱势）

2. **Supertrend** (4%): 趋势跟踪。
   - 加分: 收盘价在 Supertrend 线上方且方向向上
   - 扣分: 收盘价在 Supertrend 线下方

3. **HMA 方向** (4%): Hull Moving Average 方向。
   - 加分: HMA(16) 斜率向上且价格在 HMA 上方
   - 扣分: HMA 斜率向下

4. **量比** (3%): 当前成交量 / 过去 20 日平均成交量。
   - 加分: 量比 > 1.5
   - 扣分: 量比 < 0.5

#### L3 结构 (15%) — 结构支撑

1. **RSI 健康区** (5%): RSI(14) 处于 40-70 的健康区间。
   - 加分: 40 < RSI < 70
   - 扣分: RSI > 80（超买）或 RSI < 30（超卖）
   - 否决项: RSI 极端 30 以下或 80 以上，额外扣 20 分（见否决项）

2. **DMI(+DI / -DI)** (5%): 趋向指标。
   - 加分: +DI > −DI 且 ADX > 20
   - 扣分: +DI < −DI

3. **前高突破** (5%): 当前价格突破过去 20 日高点。
   - 加分: 收盘价 > 过去 20 日最高价 × 0.995
   - 扣分: 收盘价 < 过去 10 日最低价

#### L4 确认 (15%) — 最终确认

1. **Donchian 突破** (5%): 价格突破 Donchian 通道上轨。
   - 加分: 收盘价 > Donchian(20) 上轨
   - 扣分: 收盘价 < Donchian(10) 下轨

2. **均线排列** (5%): 短期、中期、长期均线多头排列。
   - 加分: MA5 > MA20 > MA60
   - 扣分: MA5 < MA20 < MA60

3. **MACD 金叉** (5%): DIF 上穿 DEA。
   - 加分: MACD 柱状线由负转正或最近 3 日内出现金叉
   - 扣分: MACD 柱状线持续缩小且 DIF 在 DEA 下方

### 4. Veto Rules (否决项)

After calculating the 4-layer composite score, apply the following veto deductions. The final score cannot fall below 0.

| Veto Item | Trigger | Penalty | Notes |
|-----------|---------|---------|-------|
| **ADX too low** | ADX(14) < 15 | −20 | Trend strength too weak; avoid entering |
| **RSI extreme** | RSI(14) < 30 or RSI(14) > 80 | −20 | Overbought/oversold condition; wait for reversion |
| **OI divergence** | Price makes new high but OI decreases, or vice versa | −20 | Smart money disagreement; requires futures OI data |
| **High fee rate** | Estimated transaction fee rate > 0.05% | −10 | Excessive cost for short-term trades |

**Veto application logic:**

1. Calculate raw 4-layer score (0-100).
2. Check each veto condition. If triggered, subtract the corresponding penalty.
3. Final score = max(0, raw_score − total_veto_penalty).
4. Use the final score for signal generation and position sizing.

**Important:** Veto rules are applied only in the 4-layer framework. If using the 6-category framework, the existing risk management thresholds (stop loss, take profit) and score distribution rules apply instead.

### 5. Dynamic Threshold Trading Signals

**Buy Signal (Add to Position):**
- Composite score rises above the 80th percentile of the universe
- Or score improves by >20 points from previous period
- Additional condition: score > 70 (out of 100)

**Sell Signal (Reduce/Clear Position):**
- Composite score falls below the 20th percentile of the universe
- Or score declines by >20 points from previous period
- Additional condition: score < 30 (out of 100)

**Position Sizing:**

Position size is proportional to the composite score:

```
Position Size (%) = (Composite Score - 50) / 50 * Max_Position_Size
```

Example: If max position size is 10% and score is 80, position size = (80-50)/50 * 10% = 6%.

### 6. Multi-Market Support

**A-Shares (China):**
- Data source: `akshare` library
- Trading hours: 9:30-11:30, 13:00-15:00 (Beijing time)
- T+1 settlement, 10% price limit (main board)
- Account: Required (user may provide access)

**HK Stocks:**
- Data source: `akshare`, `yfinance`
- Trading hours: 9:30-12:00, 13:00-16:00 (Hong Kong time)
- No price limit, T+2 settlement

**US Stocks:**
- Data source: `yfinance`, `akshare`
- Trading hours: 9:30-16:00 (EST), pre/post market available
- No price limit, T+2 settlement

**Futures / Derivatives (for 4-Layer Framework):**
- Data source: `akshare` futures module, `yfinance` for commodity/Index futures
- OI (Open Interest) data: typically available only for futures/options contracts; for single stocks, use volume growth as a proxy
- Example symbols: `IF2506.CCFX` (CSI 300 futures), `RB2510.SHF` (rebar futures), `GC=F` (COMEX gold)
- Fee rate: futures commission rates vary by broker; use actual rate in `VETO_RULES['high_fee_rate']`
- 4-layer framework is best suited for liquid index futures, commodity futures, and ETF options

**Data Availability Notes for OI:**
- A-share stocks do not publish real-time Open Interest. When running the 4-layer framework on A-shares, the `oi_change_rate` factor should be replaced by `volume_5d_growth_rate` or `turnover_change_rate`.
- For HK and US single stocks, OI is generally unavailable; use volume-based proxies.
- For futures/options contracts, OI is usually available in end-of-day or real-time market data feeds.

### 7. Multi-Timeframe Support

The system supports four timeframes:

| Timeframe | Use Case | Indicator Parameters |
|-----------|----------|---------------------|
| Daily | Swing trading (hold 5-20 days) | MA20, MA60, MACD(12,26,9) |
| 4H | Medium-term trend | MA50, MA200, RSI(14) |
| 1H | Short-term entries | MA20, Bollinger Bands(20,2) |
| 15M | Intraday timing | MA10, RSI(14), volume spikes |

Each timeframe has its own scoring calculation. Signals are generated by combining timeframes (e.g., daily score >70 AND 4H score >60 = strong buy).

### 8. Workflow

**Step 1: Data Collection**

To collect market data for scoring:

```python
from data_loader import MultiMarketDataLoader

loader = MultiMarketDataLoader()
data = loader.load_data(
    symbols=['600519.SH', '000858.SZ', 'AAPL', '0700.HK'],
    start_date='2024-01-01',
    end_date='2024-12-31',
    timeframe='daily'  # or '4h', '1h', '15m'
)
```

**Step 2: Calculate Factor Scores**

To calculate scores for each stock:

```python
from scoring_engine import MultiFactorScorer

scorer = MultiFactorScorer(factor_weights={
    'momentum': 0.25,
    'technical': 0.20,
    'volume': 0.15,
    'fundamental': 0.20,
    'macro': 0.10,
    'sector': 0.10
})

scores = scorer.calculate_scores(data)
```

**Step 3: Generate Trading Signals**

To generate buy/sell signals based on dynamic thresholds:

```python
from signal_generator import SignalGenerator

generator = SignalGenerator(
    buy_threshold_percentile=80,
    sell_threshold_percentile=20,
    score_improvement_threshold=20
)

signals = generator.generate_signals(scores, historical_scores)
```

**Step 4: Backtest**

To backtest the strategy:

```python
from backtest import BacktestEngine

engine = BacktestEngine(
    initial_capital=100000,
    commission=0.0003,  # 0.03%
    slippage=0.001  # 0.1%
)

results = engine.run_backtest(data, signals, scores)
engine.print_results()
engine.plot_results()
```

**Step 5: Simulate Trading**

To run simulated trading:

```python
from simulated_broker import SimulatedBroker

broker = SimulatedBroker(initial_capital=100000)
broker.execute_signals(signals, data)
broker.print_portfolio_summary()
```

### 9. File Structure

To use this skill, create the following files:

```
multi_factor_scoring/
├── data_loader.py          # Multi-market data loading (A-shares, HK, US)
├── scoring_engine.py       # Multi-factor scoring calculation
├── signal_generator.py     # Dynamic threshold signal generation
├── backtest.py             # Backtest engine
├── simulated_broker.py    # Simulated trading execution
├── visualization.py        # Plotting and reporting
├── config.py               # Configuration (weights, thresholds, symbols)
└── main.py                 # Main execution script
```

### 10. Dependencies

To install required libraries:

```bash
pip install pandas numpy matplotlib seaborn ta akshare yfinance scikit-optimize
```

**Key Libraries:**
- `pandas`, `numpy`: Data manipulation
- `matplotlib`, `seaborn`: Visualization
- `ta`: Technical indicators
- `akshare`: A-share and HK stock data
- `yfinance`: US stock data
- `scikit-optimize`: Parameter optimization (optional)

### 11. Configuration Example

To customize the strategy, edit `config.py`:

```python
# Factor weights (must sum to 1.0)
FACTOR_WEIGHTS = {
    'momentum': 0.25,
    'technical': 0.20,
    'volume': 0.15,
    'fundamental': 0.20,
    'macro': 0.10,
    'sector': 0.10
}

# Trading universe
SYMBOLS = {
    'ashare': ['600519.SH', '000858.SZ', '601318.SH'],  # Moutai, Wuliangye, Ping An
    'hk': ['0700.HK', '0941.HK', '9988.HK'],  # Tencent, China Mobile, Alibaba
    'us': ['AAPL', 'MSFT', 'GOOGL']
}

# Timeframes to use
TIMEFRAMES = ['daily', '4h', '1h', '15m']

# Signal generation thresholds
BUY_THRESHOLD_PERCENTILE = 80
SELL_THRESHOLD_PERCENTILE = 20
SCORE_IMPROVEMENT_THRESHOLD = 20  # points

# Risk management
MAX_POSITION_SIZE = 0.10  # 10% per stock
MAX_SECTOR_EXPOSURE = 0.30  # 30% per sector
STOP_LOSS = 0.08  # 8% stop loss
TAKE_PROFIT = 0.20  # 20% take profit
```

**4-Layer Framework Config Example:**

```python
# 4-Layer scoring framework (for trend-sprout timing / futures)
SCORING_FRAMEWORK = "4-layer"

LAYER_WEIGHTS = {
    'sprout': 0.55,       # L1 萌芽
    'volume_price': 0.15, # L2 量价
    'structure': 0.15,    # L3 结构
    'confirmation': 0.15  # L4 确认
}

# L1 萌芽 indicators
SPROUT_FACTORS = {
    'oi_change_rate': 0.15,      # OI 变化率 (stocks: use volume growth as proxy)
    'atr_percentile': 0.15,      # ATR 百分位
    'obv_trend': 0.15,           # OBV 趋势
    'cmf': 0.10                 # Chaikin Money Flow
}

# L2 量价 indicators
VOLUME_PRICE_FACTORS = {
    'cci': 0.04,                 # CCI(14)
    'supertrend': 0.04,          # Supertrend direction
    'hma_direction': 0.04,       # HMA(16) direction
    'volume_ratio': 0.03        # 量比
}

# L3 结构 indicators
STRUCTURE_FACTORS = {
    'rsi_health_zone': 0.05,     # RSI(14) 40-70 zone
    'dmi_plus_minus_di': 0.05,   # DMI +DI/-DI spread
    'new_high_breakout': 0.05    # Breakout above 20-day high
}

# L4 确认 indicators
CONFIRMATION_FACTORS = {
    'donchian_breakout': 0.05,   # Donchian channel breakout
    'ma_alignment': 0.05,        # MA5 > MA20 > MA60
    'macd_golden_cross': 0.05   # MACD golden cross
}

# Veto rules (deducted from raw 4-layer score)
VETO_RULES = {
    'adx_too_low': {'trigger': 'ADX(14) < 15', 'penalty': -20},
    'rsi_extreme': {'trigger': 'RSI(14) < 30 or RSI(14) > 80', 'penalty': -20},
    'oi_divergence': {'trigger': 'Price new high but OI decreases', 'penalty': -20},
    'high_fee_rate': {'trigger': 'fee_rate > 0.0005', 'penalty': -10}
}

# 4-layer framework thresholds
LAYER_BUY_THRESHOLD = 70
LAYER_SELL_THRESHOLD = 30
```

### 12. Output and Reporting

The system generates the following outputs:

**Trading Signals:**
- Current buy/hold/sell recommendations for each stock
- Composite scores and factor breakdowns
- Signal strength (weak/moderate/strong)

**Portfolio:**
- Current positions and scores
- P&L for each position
- Portfolio composite score

**Performance:**
- Backtest results (returns, Sharpe ratio, max drawdown)
- Benchmark comparison (CSI 300, Hang Seng, S&P 500)
- Factor contribution analysis

**Visualization:**
- Score heatmap (stocks × factors)
- Portfolio composition pie chart
- Equity curve with benchmark
- Factor exposure breakdown

## 13. Latest Research Integration (2026 arXiv Papers)

This skill now incorporates cutting-edge research from 12 top arXiv papers (May–July 2026). These features are enabled by default and can be toggled in `scoring_engine.py`, `volatility_forecaster.py`, `uncertainty_quantification.py`, and `simulated_broker.py`.

### 13.1 Market Impact Model (arXiv:2606.24019)

**Paper:** "Empirical Confirmation of the Square-Root Law of Market Impact in U.S. Large-Cap Equity"

**Implementation:** Added to `scoring_engine.py` as `_calculate_market_impact_adjustment()`

**Square-Root Law:**
```
Market Impact ∝ √(Q / V_D)
```
Where:
- Q = Order size (shares)
- V_D = Daily trading volume (shares)

**Usage:**
```python
scorer = MultiFactorScorer(
    enable_market_impact=True  # Enable market impact adjustment
)

# Calculate scores with position sizes (for impact adjustment)
position_sizes = {'600519.SH': 1000, '000858.SZ': 500}
scores = scorer.calculate_scores(data, fundamentals, macro, position_sizes)
```

**Effect:** High market impact orders (large relative to daily volume) receive a score penalty (up to 30% reduction) to account for execution difficulty.

---

### 13.2 Dynamic Transaction Cost Optimization (arXiv:2606.21784)

**Paper:** "KineticSim: A Lightweight, High-Performance Execution Engine for Real-Time Market Simulators"

**Implementation:** Added to `simulated_broker.py` as `_calculate_dynamic_commission()` and `_calculate_dynamic_slippage()`

**Features:**
1. **Dynamic Commission:** Adjusts commission based on:
   - Order size relative to daily volume (square-root law)
   - Market volatility (higher vol = higher commission)
   - Caps at 3x base commission

2. **Dynamic Slippage:** Adjusts slippage based on:
   - Order size vs. liquidity
   - Caps at 1% slippage

**Usage:**
```python
broker = SimulatedBroker(
    initial_capital=100000,
    enable_dynamic_costs=True  # Enable dynamic cost optimization
)

# Execute signals (pass data for dynamic cost calculation)
broker.execute_signals(signals, data)
```

**Effect:** Larger orders in illiquid stocks incur higher transaction costs, reducing unrealistic profits in backtests.

---

### 13.3 Adaptive Regime Detection (arXiv:2606.23596)

**Paper:** "Anatomy of the Market: A Body-Tail Test of Factor Models"

**Implementation:** Added to `scoring_engine.py` as `_detect_regime()` and `_apply_regime_adjustment()`

**Detected Regimes:**
- `'bull'`: Low volatility, positive returns → Boost momentum + technical factors
- `'bear'`: High volatility, negative returns → Boost fundamental + macro factors
- `'normal'`: Moderate volatility/returns → Balanced weights
- `'crisis'`: Extreme volatility → Boost volume + sector factors (defensive)

**Usage:**
```python
scorer = MultiFactorScorer(
    enable_regime_detection=True  # Enable regime detection
)

# Regime is automatically detected during calculate_scores()
scores = scorer.calculate_scores(data, fundamentals, macro)

print(f"Current regime: {scorer.current_regime}")
print(f"Regime confidence: {scorer.regime_confidence:.2f}")
```

**Effect:** Factor weights dynamically adjust based on market regime, improving performance across different market conditions.

---

### 13.4 Robust Bayesian Portfolio Selection (arXiv:2606.24212)

**Paper:** "Path Space Robust Bayesian Portfolio Selection"

**Status:** ⚠️ **Disabled by default** (requires >16GB RAM for Kalman filter optimization)

**To Enable:**
```python
scorer = MultiFactorScorer(
    enable_robust_bayesian=True  # Enable Robust Bayesian (requires cloud GPU)
)
```

**Note:** This feature is computationally intensive. For your hardware (i3-4170 + 4GB RAM), we recommend using cloud GPU (Google Colab, AWS, etc.) to run this module.

---

### 13.5 Excluded Papers (Not Relevant)

The following papers were excluded from integration:
- **arXiv:2606.23070, arXiv:2606.21769**: AMM dynamic fees (cryptocurrency, not stocks)
- **arXiv:2605.23007**: MadEvolve (LLM evolution, requires >16GB RAM)
- **arXiv:2605.05580, arXiv:2605.12532**: Multi-agent frameworks (requires >16GB RAM)

---

### 13.6 Realized-Volatility Forecasting: Log-HAR + TTM Equal-Weight Ensemble (arXiv:2607.05291)

**Paper:** "Forecasting Realized Volatility with Time Series Foundation Models: A Comparison with Econometric Benchmarks" — Brini (2026)

**Why this matters for your 5-factor WQUANT system:** In the 波动率 (volatility) dimension, the instinct is to reach for a large time-series foundation model (TSFM). This paper shows that is the wrong instinct.

#### Key empirical findings (VOLARE dataset, 50 assets, 3 horizons)

| Finding | Implication for WQUANT |
|---------|------------------------|
| 9 zero-shot TSFMs vs 8 econometric benchmarks (HAR family) — **no uniform win** for foundation models | Don't assume "bigger model = better volatility forecast" |
| Only **Tiny Time Mixers (TTM)** — a <1M-param model — beats Log-HAR at every horizon, by a **narrow margin** | A tiny model is enough; skip the heavyweights |
| Short-horizon gains come mostly from **better scale calibration** (Mincer-Zarnowitz), not better volatility-dynamics modelling | The "edge" is mostly debiasing the level/scale, not skill |
| **Equal-weight TTM + Log-HAR ensemble** enters the Model Confidence Set (MCS) for **98–100%** of assets — more often than either alone | Ensemble >> single best model; no need to pick per-asset winner |
| Architecture choice matters more than foundation-vs-econometric choice | Pick the right small model, not "a foundation model" |

#### Implementation (in `scripts/volatility_forecaster.py`)

Three components, composable:

1. **`LogHAR`** — log-Heterogeneous Autoregressive realized-volatility forecaster (Corsi 2009, log spec).
   - `log(RV_t) = b0 + b_d·log(RV_{t-1}) + b_w·log(mean RV_{t-1..t-5}) + b_m·log(mean RV_{t-1..t-22}) + e_t`
   - RV computed from daily (log) returns: `RV_t ≈ ret_t²` (use intraday bars when available for the exact `Σ r²`).
   - Multi-step `h`-day forecast by recursion. OLS via `np.linalg.lstsq`.

2. **`TTMForecaster`** — IBM TinyTimeMixer, zero-shot, lightweight (<1M params).
   - Package: `pip install granite-tsfm` (provides `tsfm_public`); model `ibm/TTM`.
   - Zero-shot: no fine-tuning. Runs on CPU; fits the low-RAM machine.
   - Loaded **lazily** and **only if enabled** — the skill works without it.

3. **`EnsembleVolForecaster`** — the durable result:
   - `RV_forecast_h = 0.5 · LogHAR_h + 0.5 · TTM_h`
   - **Graceful degradation**: if TTM is unavailable (package missing / load fails), it falls back to Log-HAR only and sets `ttm_available = False`.
   - Optional **Mincer-Zarnowitz recalibration** (`recalibrate=True`): removes level/scale bias using in-sample LogHAR errors (no lookahead into the forecast target).

**Mapping to the volatility dimension (0–100 score):**
`volatility_score_from_forecast()` returns the percentile of the h-day-ahead forecasted RV within the trailing 60-day distribution. Semantics match the 4-Layer **L1 ATR-percentile**: higher future volatility ⇒ higher score (vol expansion = breakout opportunity). This makes it a drop-in enhancement for L1's volatility read, or the standalone 波动率 factor in a 5-factor system.

#### Usage

```python
from volatility_forecaster import EnsembleVolForecaster, realized_variance, volatility_score_from_forecast

# From daily returns (or pass RV directly with as_rv=True)
ef = EnsembleVolForecaster(use_ttm=True, recalibrate=False)
forecast_rv = ef.forecast(daily_returns, h=5)          # 5-day-ahead RV
score = volatility_score_from_forecast(forecast_rv, realized_variance(daily_returns))
print(f"TTM used: {ef.ttm_available}, vol score: {score:.1f}")
```

**Plug into the scorer (opt-in, config-driven):**

```python
# config.py
ENABLE_VOL_FORECAST = True    # adds a 'volatility' column to scores
VOL_HORIZON = 5               # 1 (daily) / 5 (weekly) / 22 (monthly)
VOL_USE_TTM = True            # needs `pip install granite-tsfm`
VOL_CONTEXT_LENGTH = 64
VOL_RECALIBRATE = False       # Mincer-Zarnowitz scale debiasing

# scoring_engine.py
scorer = MultiFactorScorer(enable_vol_forecast=True)   # reads config by default
scores = scorer.calculate_scores(data)
# scores['600519.SH']['volatility']  -> 0-100 volatility-dimension score
```

**Integration paths:**
- **WQUANT 5-factor (趋势/成交量/市场宽度/资金流向/波动率):** use `scores[symbol]['volatility']` directly as the 波动率 dimension.
- **4-Layer L1 萌芽:** replace/augment the ATR-percentile sub-score with this forecast-based percentile for a forward-looking volatility read (current ATR = now; this = next h days).

**Caveats (from the paper):**
- TTM is **not** best on every asset — the ensemble, not TTM alone, is the robust choice.
- At the monthly horizon a genuine informational gain remains; at short horizons most of the gain is scale calibration.
- Validate `TTMForecaster` output on your machine once `granite-tsfm` is installed — the `tsfm_public` pipeline column names can vary across versions (handled defensively in code).

---

### 13.7 Distribution-Free Uncertainty Quantification: Bootstrap + Conformal CIs for Signals (arXiv:2607.06690)

**Paper:** "tsbootstrap: Distribution-Free Uncertainty Quantification and Conformal Prediction for Time Series" — Gilda (2026)

**Why this matters for your signals:** A point forecast (factor return, forecasted volatility, composite score) tells you *where*, never *how sure*. Sizing positions off a point estimate that sits inside the noise band is the classic risk trap. This module attaches a **calibrated confidence interval** to each signal, then turns interval width into a **position-confidence multiplier** and a **risk gate**.

#### Key empirical findings

| Finding | Implication for WQUANT |
|---------|------------------------|
| The **IID bootstrap undercovers sharply** under serial dependence | Never quantify a serially-dependent signal (returns, RV) with an IID bootstrap — intervals will be too tight and you'll over-size |
| **Dependence-aware** resampling (block / sieve) restores coverage near nominal; sieve nearest under short-memory linear dependence | Default to a **moving-block** bootstrap for financial signals |
| **Conformal calibration** gives a finite-sample coverage guarantee; adaptive variants (**EnbPI / ACI / NexCP / AgACI**) hold coverage on drifting streams | Use conformal for forecast prediction intervals; adaptive variants when the stream drifts |
| One typed API combines a dependence-aware resampling engine with an adaptive conformal layer | Single mental model: pick a *method spec*, get calibrated intervals |

#### Implementation (in `scripts/uncertainty_quantification.py`)

Distribution-free, with the same graceful-fallback pattern as the volatility module:

1. **`moving_block_bootstrap` / `auto_block_length`** — dependence-aware resampler. Block length picked from the first insignificant ACF lag (2/√n band) with an n^(1/3) floor — the block must span the memory of the series to restore coverage.
2. **`bootstrap_ci`** — distribution-free CI for *any* statistic (default: mean). **PRIMARY path** uses `tsbootstrap` `MovingBlock(block_length="auto")` (Politis–White) if installed; **FALLBACK** is the pure-numpy moving-block resampler. The statistic + percentile interval are always computed here, so results are correct regardless of backend.
3. **`conformal_halfwidth`** — split-conformal half-width `Q_{⌈(n+1)(1-α)⌉/n}(|residuals|)`; ≥ (1−α) marginal coverage under exchangeability, degrades gracefully on dependent streams (use block/adaptive conformal via `tsbootstrap.uq` for strict coverage).
4. **`position_confidence`** — maps relative CI width to a sizing multiplier: `clip( 1/(1 + k·rel_width), floor, 1 )`. Narrow CI ⇒ near 1 (full size); wide CI ⇒ near `floor` (shrink).
5. **`risk_gate`** — significance / risk-threshold decision on an expected-return CI. If the CI straddles zero the edge is indistinguishable from noise → veto (or scale down).
6. **`quantify_signal`** — one-call bundle: CI + confidence + risk gate.

**Install for the primary (dependence-aware) path:** `pip install tsbootstrap` (MIT, v0.6.1). Without it the module runs on numpy alone (`backend="numpy-fallback"`).

#### Usage

```python
from uncertainty_quantification import quantify_signal, signal_confidence_interval, position_confidence

# CI on the mean of a signal (factor returns, forecasted RV, ...)
ci = signal_confidence_interval(daily_returns, alpha=0.10)   # 90% CI, moving-block
# {'point':..., 'lower':..., 'upper':..., 'rel_width':..., 'backend':...}

conf = position_confidence(ci['rel_width'])                  # -> [0.30, 1.0] sizing multiplier

bundle = quantify_signal(daily_returns, alpha=0.10, direction="long", require_significant=True)
# bundle['confidence'], bundle['risk_gate']['significant'/'veto'/'scale']
```

**Plug into the scorer (opt-in, config-driven):**

```python
# config.py
ENABLE_UNCERTAINTY = True     # adds confidence/ci_low/ci_high/edge_significant/risk_scale columns
UQ_ALPHA = 0.10               # (1 - alpha) = 90% intervals
UQ_N_BOOTSTRAPS = 500
UQ_CONF_FLOOR = 0.30
UQ_REQUIRE_SIGNIFICANT = False  # True -> veto (scale->0) when the return CI straddles zero

# scoring_engine.py
scorer = MultiFactorScorer(enable_uncertainty=True)   # reads config by default
scores = scorer.calculate_scores(data)
# scores['600519.SH']['confidence']       -> position-sizing multiplier [0.30, 1]
# scores['600519.SH']['edge_significant'] -> True if CI on mean return excludes 0
```

**Integration paths:**
- **Position sizing:** multiply your target weight by `confidence` (or `risk_scale`). Precise signals get full size; noisy signals get shrunk — a distribution-free alternative to ad-hoc conviction weighting.
- **Risk-control threshold:** gate entries on `edge_significant` (CI excludes zero). Combine with the 4-Layer veto rules as an extra "signal is real, not noise" filter.
- **Volatility dimension:** wrap the Log-HAR + TTM forecast (§13.6) with `conformal_halfwidth` on its in-sample residuals to publish a *prediction interval* on next-h-day RV, not just a point.

**Caveats (from the paper):**
- The **IID bootstrap is the wrong default** for dependent signals — always use the moving-block (or sieve) path. The module defaults to moving-block for this reason.
- Split conformal assumes exchangeability; on strongly drifting streams prefer adaptive conformal (EnbPI/ACI/NexCP/AgACI) via `tsbootstrap.uq`.
- Wider `n_bootstraps` = smoother intervals but slower; 500 is a good balance for per-symbol scoring.

---

### 13.8 This-Week arXiv Integration (2026-07-14 ~ 2026-07-18)

Crawled the arXiv **q-fin** recent listing (announcements 2026-07-14 → 2026-07-17) plus cross-listings; scanned 50+ titles and selected 6 with a direct, non-speculative mapping to this skill's modules. Each adds a concrete signal/factor or strengthens an existing module. Follows the opt-in, config-driven, graceful-fallback pattern of §13.6/§13.7.

#### 13.8.1 Signal→Cost-Aware Multi-Period Allocation (arXiv:2607.15195)

**Paper:** "SciPhy Reinforcement Learning for Portfolio Optimization" — Halperin & Itkin (2026-07-16)

**Key findings:** Formulates portfolio optimization as continuous-time Scientific Physics-Informed RL (SciPhy-RL). A pathwise HJB is solved via PINN in a *single offline sweep* (no value/policy iteration). The control is recast from a continuous trading rate to a **discrete target holding**, so signal-implied positions are reached immediately, while execution cost is priced with a microstructure-grounded quadratic price-impact model. On a 14-asset ETF universe with an engineered oracle signal, the learned Gibbs policy yields substantial **out-of-sample Sharpe improvement** over static/myopic baselines, with strictly controlled volatility and turnover.

**Framework mapping:** Strengthens the **Position Sizing** block (§5) and the dynamic-cost module (§13.2). Current sizing is a single-period linear rule `size = (score-50)/50*max`; this paper turns a *given signal* into an optimal **cost-aware, multi-period holding path**.

**Signal design:** Add `cost_aware_allocate(scores, cost_model)` to `simulated_broker.py`:
- Input: composite scores (signal quality) + quadratic price-impact cost estimate (from §13.2).
- Output: discrete target weights per asset, solved offline (PINN/HJB) once per rebalance, then applied as target holdings.
- Feed the current linear sizing in as the *signal* to this allocator, not as the final weight.
- Risk control: cap turnover (paper shows controlled turnover) and bound volatility using the §13.6 forecast as the vol constraint.

**Caveat:** PINN/HJB solve is offline + compute-heavy; default **OFF** (same guidance as §13.4). The portable takeaway is the **discrete-target-holding recast** — prefer it over continuous trading-rate control in backtests to avoid execution look-ahead.

---

#### 13.8.2 Base-Rate-Honest Significance Test for ML Forecast Signals (arXiv:2607.12248)

**Paper:** "When Directional Accuracy Lies: A Base-Rate-Honest Benchmark for LoRA-Adapted TimesFM on Equity Forecasting" — Cheung (2026-07-15)

**Key findings:** Directional-accuracy metrics for time-series foundation models (TimesFM, LoRA-adapted) on equity forecasting are misleading when the market's up/down **base rate** is ignored. A model can post high "directional accuracy" yet add no value vs a naive base-rate classifier. Directly reinforces the §13.6 warning that TSFMs are not automatically superior.

**Framework mapping:** Strengthens the **Uncertainty Quantification** module (§13.7), specifically `edge_significant` and `risk_gate`. Adds a base-rate-honest layer on top of the moving-block CI.

**Signal design:** Extend `uncertainty_quantification.py` with `base_rate_honest_significance()`:
- Compute the market's empirical up/down base rate `p0` over the trailing window.
- For a directional ML signal, test whether its hit rate `p̂` exceeds `p0` by more than the CI half-width allows: significant only if `p̂_lower > p0`.
- Feed into `risk_gate`: if the directional signal is **not** base-rate-honest-significant, push `risk_scale` toward floor (don't size on a signal that beats chance only by noise).
- Guards the volatility forecast (§13.6) and any TSFM-based factor from being over-trusted on directional calls.

**Caveat:** Base rate must use the **same labeling horizon** as the signal (next-day vs next-5d up differ). Mismatch → false significance.

---

#### 13.8.3 Denoised Correlation-Breadth Factor (arXiv:2607.10297)

**Paper:** "Recovering Structural Organization in Noisy Correlation Networks Using Financial Systems as a Testbed" — Ansari, Jain & Iyer (2026-07-14)

**Key findings:** Financial correlation matrices are noisy; structural organization (blocks/clusters) can be recovered from noisy correlation networks via a denoising method. The recovered structure is a more stable basis for breadth/sector-comovement than raw correlations.

**Framework mapping:** Strengthens the **Sector/Industry** factor (§2) and the **regime-detection** input (§13.3). Supplies a denoised correlation matrix for breadth and sector-rotation reads.

**Signal design:** Add `denoised_correlation_breadth(prices)` to `scoring_engine.py`:
- Build the trailing correlation matrix from returns, denoise (recover block structure), then compute **market breadth** = fraction of assets with positive denoised comovement to the market eigenvector, and **sector coherence** = intra-cluster correlation strength.
- Use breadth as a regime input (`crisis` when breadth collapses) and as a sector-factor sub-score.
- Replaces naive equal-weight breadth with a structure-aware read → less whipsaw in regime calls.

**Caveat:** Denoising window must be long enough to estimate the correlation block structure; short windows → unstable clusters. Use **≥ 60 observations**.

---

#### 13.8.4 Leading Indicator for Crisis Regime: Eigenvector-Rotation Early-Warning (arXiv:2607.11935)

**Paper:** "Eigenvector rotation precedes eigenvalue-based early-warning signals: a TVP-Kalman approach to detecting critical transitions" — Ngueuleweu (2026-07-15)

**Key findings:** In systems approaching a critical transition, the **rotation of eigenvectors** (loadings) *leads* the eigenvalue-based early-warning signals. A time-varying-parameter Kalman filter detects this rotation earlier than traditional variance/eigenvalue metrics.

**Framework mapping:** Strengthens **Adaptive Regime Detection** (§13.3), adding an *early-warning* layer that flips `crisis` detection from reactive (volatility spike) to **leading** (eigenvector rotation in the return covariance).

**Signal design:** Add `covariance_early_warning(returns)` to `scoring_engine.py` (feeds `_detect_regime()`):
- Track the *rate of eigenvector rotation* of the rolling covariance via TVP-Kalman (or a cheap proxy: week-over-week change in top-PC loadings).
- When rotation accelerates beyond a trailing threshold while eigenvalues are still calm → raise `crisis_warning=True` (leading indicator), tightening the 4-Layer veto / shrinking `risk_scale` **before** vol explodes.
- Combine with §13.3: rotation-warning promotes a defensive weight tilt (volume + sector) earlier.

**Caveat:** TVP-Kalman is the heavy part; default to the **proxy** (top-PC loading change), full Kalman opt-in.

> ⚠️ **Partially superseded — read §13.10.2 before using this as a leading indicator.** arXiv:2607.27070 (2026-07-29) shows the entire critical-slowing-down family (variance, AC(1), eigenvalue **and** eigenvector-rotation) is **event-heterogeneous**: it fires on endogenous-buildup cascades but is structurally silent on exogenous shocks. Treat this subsection's output as a population-level prior with a capped effect on `risk_scale`, never as the sole tail defence. See constraint #31.

---

#### 13.8.5 Fat-Tail-Aware Risk Gate (arXiv:2607.10810)

**Paper:** "Diachronic Sample Integration: Robust Tail-Risk Estimation with Generative Models" — Zhao et al. (2026-07-14)

**Key findings:** Standard tail-risk estimates understate risk when the sample is non-stationary; a *diachronic* (time-aware) sample-integration with generative models gives more robust tail-risk (VaR/CVaR) estimates than i.i.d. historical sampling.

**Framework mapping:** Strengthens the **Uncertainty Quantification** risk gate (§13.7) and drawdown control. Augments `risk_gate` with a fat-tail-aware CVaR check that respects time structure — pairs naturally with the moving-block bootstrap in §13.7 (which already forbids IID resampling).

**Signal design:** Extend `uncertainty_quantification.py` with `tail_risk_gate(returns, alpha)`:
- Estimate CVaR using **time-aware (block/diachronic)** sampling, not i.i.d. historical.
- If CVaR (scaled to position) breaches the user's loss budget → veto/scale-down the position even when the point signal is positive.
- Reuses the moving-block backend from §13.7 (no IID), consistent with the no-IID rule (constraint #11).

**Caveat:** Generative tail-model is opt-in (compute); the time-aware block-CVaR is the default and needs no ML.

---

#### 13.8.6 News-Sentiment Alternative Factor (arXiv:2607.13968)

**Paper:** "Measuring Sentiment News with Transformer-Based Language Models" — Mavillonio et al. (2026-07-16)

**Key findings:** Transformer-based LMs measure news sentiment reliably; a news-sentiment score is a tradable alternative-data signal that leads price action when integrated as a factor.

**Framework mapping:** Adds an **alternative-data** input to the **Fundamentals** factor (§2) / composite score — a news-sentiment sub-score, distinct from the price/volume technical factors.

**Signal design:** Add `news_sentiment_score(news_texts)` (pluggable; default = transformer sentiment score, cached daily):
- Map sentiment ∈ [-1, 1] to a 0–100 sub-score; blend into the composite with a small weight (e.g., 5% of the fundamentals bucket, or a standalone alt-data column).
- Use as a *confirmation* overlay: strongly negative news-sentiment can apply a soft veto on buy signals (narrative risk), without replacing the price-based 4-Layer score.
- For crypto/derivatives, pair with on-chain sentiment (arXiv:2607.15258 "Decoding Market Emotion from Blockchain Activity") as a crypto-specific sentiment factor.

**Caveat:** News sentiment is slow vs price; treat as a **low-frequency overlay**, not an intraday signal. Avoid double-counting with momentum.

---

### 13.9 This-Week arXiv Integration (2026-07-20 ~ 2026-07-24)

Crawled the arXiv **q-fin** recent listing (announcements 2026-07-20 → 2026-07-24, 64 papers) plus cross-listings; scanned all titles and selected 6 with a direct, non-speculative mapping to this skill's modules. Follows the opt-in, config-driven, graceful-fallback pattern of §13.6–§13.8. This week's theme is **evaluation honesty + trend theory**: three papers are rigorous *audits* of popular signals, two upgrade risk/diversification machinery, one gives closed-form trend-following theory.

#### 13.9.1 Analytical Trend-Following Design: Spectral-Mass Alpha & Cost-Optimal Span (arXiv:2607.19497)

**Paper:** "The Science and Practice of Trend-Following Systems" — Sepp & Lucic (2026-07-23)

**Key findings:** Unified theory of TF systems (European / American / TSMOM). Exact P&L ↔ autocorrelation ↔ drift relation in vol-normalized returns; TF is profitable when long-term autocorrelation is positive **even under short-term mean reversion**. In the frequency domain, TF alpha = **excess spectral mass at low frequencies** (Poisson-kernel reading of the spectrum). Closed-form Sharpe (excess kurtosis enters via a single loading), closed-form **cost-optimal lookback span** under trading costs, and structurally **positive skewness** of TF returns peaking near half the filter span. All TF variants are strongly correlated empirically.

**Framework mapping:** Strengthens the **Momentum** factor (§2) and the 4-Layer **L2 量价** trend reads (Supertrend/HMA). Replaces ad-hoc lookback choice with a principled one.

**Signal design:** Add `trend_quality_diagnostic(returns)` to `scoring_engine.py`:
- Estimate the low-frequency spectral mass of vol-normalized returns (Welch periodogram, kernel-weighted); sub-score = percentile of excess low-freq mass vs universe. High mass ⇒ trend-followable asset ⇒ boost momentum weight for that symbol.
- Select the momentum lookback as the **cost-optimal span** given the asset's estimated cost (reuse §13.2 dynamic costs) instead of fixed 20/60/120.
- Position management: TF positive skew is structural — avoid tight stop-losses that truncate the right tail (document in risk config).

**Caveat:** Spectral estimates need ≥ 250 obs to be stable; below that fall back to fixed spans.

---

#### 13.9.2 Triple-Gate Factor Admission: Statistical × Economic × Survival (arXiv:2607.20093)

**Paper:** "Retail Trader's Ruin: An Anatomy of Popular Signal Failure" — Darmanin (2026-07-23)

**Key findings:** Tests 5 popular retail signal families with **three predeclared gates**: (1) statistical edge after multiplicity correction (hierarchical Benjamini-Yekutieli), (2) economic viability after costs, (3) finite-bankroll survival under leverage. Result: oscillator / volume / calendar / candlestick families **REFUTED**; trend & momentum **INCONCLUSIVE** (not refuted); none SUPPORTED. Key methodology: distinguish "statistically refuted" from "unresolved" — non-significance ≠ proof of absence.

**Framework mapping:** Strengthens **§14 factor governance** (admission chain) and the S_appendix veto philosophy. The three-gate conjunction is a direct upgrade to `evaluate_factor_3level` L3.

**Signal design:** Extend `factor_governance.py` with `triple_gate_admission(factor_returns, cost_model, bankroll)`:
- Gate 1: stationary-bootstrap CI + BY-corrected p-value on the factor's exposure-matched excess return (reuses §13.7 moving-block backend).
- Gate 2: net-of-cost edge > 0 using §13.2 dynamic costs.
- Gate 3: ruin probability under the intended leverage < threshold (Kelly-fraction check).
- A factor enters the composite only if **all three gates pass**; INCONCLUSIVE factors may stay at reduced weight but must be flagged, never treated as validated.
- Down-weight prior: oscillator/candlestick/calendar-type sub-factors carry refuted-in-literature priors — require stronger evidence to admit.

**Caveat:** Gates need enough sample; small-N factors default to INCONCLUSIVE (reduced weight), not auto-admission.

---

#### 13.9.3 Calibration Benchmarking for Probabilistic Signals: Brier + Winkler (arXiv:2607.16229)

**Paper:** "FinBench: Time-Gated Calibration and Uncertainty Benchmarking for Agentic Financial Forecasting" — Ghosh & Devarakonda (2026-07-21)

**Key findings:** The critical failure mode of LLM/ML forecasters used for sizing is the **confidence–competence gap** — slightly-better-than-chance but consistently overconfident models produce negative long-run growth under bet-sizing rules. Fix: strictly **time-gated** evaluation (no look-ahead) + **strictly proper scoring rules** — Brier score for P(up), Winkler interval score for the 80% prediction interval — with skill scores vs hard baselines.

**Framework mapping:** Strengthens **§13.7 UQ** and complements the base-rate-honest test (constraint #14). Where #14 tests *direction* honesty, this tests *probability/interval* honesty.

**Signal design:** Extend `uncertainty_quantification.py` with `calibration_report(probs, intervals, outcomes)`:
- Rolling Brier + Winkler scores per signal source; skill score vs base-rate classifier and vs the §13.6 vol-forecast interval.
- Map calibration quality to the sizing multiplier: `risk_scale *= clip(brier_skill, floor, 1)` — an overconfident source gets structurally shrunk even when its point signal is strong.
- All evaluation windows strictly time-gated (train < gate < test), consistent with walk-forward (§14.2).

**Caveat:** Proper-score estimates are noisy on short windows; require ≥ 60 scored forecasts before letting calibration modify sizing.

---

#### 13.9.4 Asymmetric-Volatility CVaR Allocation & Measure Disagreement (arXiv:2607.16450)

**Paper:** "Portfolio Optimization under Heavy Tails and Asymmetric Volatility: Evidence from Taiwan-Exposed ETFs" — Lee, Shirvani, Afroz (2026-07-21)

**Key findings:** On 30 tech-concentrated ETFs (2015–2025): heavy tails everywhere, but cross-sectional differences in extreme downside risk are driven by **return scale, not tail index**; GJR-GARCH shows persistent **asymmetric** volatility, and apparent long memory in squared returns is mostly conditional heteroskedasticity. **CVaR optimization concentrates allocations** far more than mean-variance; Sharpe/STARR favor equal-weight while Rachev favors CVaR portfolios — **the measure choice changes the ranking**.

**Framework mapping:** Strengthens the **fat-tail risk gate** (§13.8.5) and the volatility dimension (§13.6). Adds sector-concentration awareness to position sizing.

**Signal design:** Extend `tail_risk_gate` in `uncertainty_quantification.py`:
- Scale CVaR by an **asymmetric-vol multiplier**: when GJR-style leverage effect is detected (down-move vol > up-move vol), inflate the loss-budget check for concentrated/tech-heavy symbols.
- For tail comparisons across symbols use **scale (VaR/CVaR level)**, not tail-index estimates — matching the paper's finding.
- Report **both** Sharpe-type and Rachev-type metrics in backtest output (§12); flag when they disagree on portfolio ranking instead of silently trusting one.

**Caveat:** CVaR-optimal weights are concentrated — always cap per-symbol/per-sector exposure (`MAX_POSITION_SIZE` / `MAX_SECTOR_EXPOSURE`) on top of CVaR optimization.

---

#### 13.9.5 Topological Diversification Distance + Retention-Based Turnover Control (arXiv:2607.21170)

**Paper:** "Portfolio Optimization under Dynamic Rebalancing via Topological Data Analysis and News Sentiments" — Garg (2026-07-24)

**Key findings:** TDA-based distance inside agglomerative clustering identifies **topologically dissimilar** assets better than correlation/Euclidean distances (captures nonlinear relations); FinBERT news sentiment adjusts for perception shifts technicals miss; a **retention mechanism** keeps high-quality assets across consecutive rebalancing windows, cutting turnover and costs. Outperforms correlation-distance and benchmark portfolios on S&P 500, robust in stress periods.

**Framework mapping:** Alternative/upgrade to the **denoised-correlation breadth factor** (§13.8.3) for the diversification step, and adds a turnover-control primitive to §13.8.1 / §5 position sizing. News-sentiment part reuses §13.8.6 (no duplication).

**Signal design:** Add `tda_diversification_clusters(prices)` to `scoring_engine.py`:
- Compute pairwise TDA distance (persistence-diagram distance on sliding-window point clouds) → agglomerative clusters → pick top-scored symbol per cluster (composite score as ranker).
- **Retention rule** in `signal_generator.py`: a held symbol is replaced only if its score falls below the challenger by a margin (e.g. > 10 pts) — hysteresis that cuts churn.
- Choice rule vs §13.8.3: denoised correlation for **regime/breadth** reads; TDA distance for **portfolio construction** diversification. Don't run both for the same purpose.

**Caveat:** TDA is compute-heavy; default to weekly cluster refresh, and fall back to denoised-correlation clustering when `giotto-tda`/`ripser` is unavailable (graceful degradation).

---

#### 13.9.6 Backtest Forensics: AUC ≠ Profit, Purged Splits, Protocol Standards (arXiv:2607.19453 + arXiv:2607.20168)

**Papers:** "Predictive Extrema, Unprofitable Policies: An AI-Assisted Audit of Candle-Based Binance Spot Timing Models" — Jadouli (2026-07-23); "Quantum Kernels and the Cross-Section of Stock Returns: Anatomy of a Vanishing Advantage" — Shen (2026-07-23)

**Key findings:** (a) Extrema classifiers hit ROC-AUC 0.87–0.90 yet **average precision only ~0.12–0.13** and lose 44% net — high AUC on imbalanced extrema labels is *not* a tradable edge; every audited policy ends NO_TRADE. Forensic failures: outcome horizon **not purged at split boundaries**, **same-close entry** (look-ahead), missing raw result directories. (b) Quantum-kernel "advantage" on A-share cross-section **vanishes** under a controlled protocol: point-in-time universe, kernel-swap controls, budget-equalized comparisons, family-wise correction — a full-sample-screened universe manufactures the opposite conclusion.

**Framework mapping:** Hardens **backtest hygiene** (§8 Step 4, §14 governance) and the ML-signal admission rules (#14, #25, #26). These are *negative results* — their value is as guard-rails, not new factors.

**Signal design:** Codify in `backtest.py` as `audit_checklist()` (run before accepting any backtest):
- [ ] Splits **purged** by at least the label horizon (+ embargo) at every boundary.
- [ ] Entry uses **next-bar open** (or later), never same-close as the signal bar.
- [ ] Imbalanced-label classifiers report **average precision + net-of-cost P&L**, never AUC alone.
- [ ] Universe is **point-in-time** (no full-sample screening before splitting).
- [ ] Model comparisons are budget-equalized with family-wise correction before claiming superiority.
- Any unchecked box ⇒ backtest result flagged UNRELIABLE and blocked from factor admission (feeds `triple_gate_admission`, §13.9.2).

**Caveat:** These checks reject bad evidence; they cannot create edge. A strategy passing all checks may still be INCONCLUSIVE (§13.9.2 taxonomy).

---

### 13.10 This-Week arXiv Integration (2026-07-27 ~ 2026-07-31)

Crawled the arXiv **q-fin** recent listing (announcements 2026-07-27 → 2026-07-31, **76 papers** incl. cross-lists); scanned all titles, read 8 abstracts, and selected 7 subsections with a direct, non-speculative mapping. Follows the opt-in, config-driven, graceful-fallback pattern of §13.6–§13.9.

This week's theme is **deployment discipline + evidence sufficiency**: three papers constrain *when you are allowed to believe or swap a model*, two upgrade the risk/cost machinery, one repairs interval coherence, one supplies an A-share-specific crowding read. Notably, §13.10.2 is a **negative result that partially retracts §13.8.4** — it is integrated as a guard-rail, not as new alpha.

#### 13.10.1 Characteristic-Driven Covariance with Zero-Shot Asset Onboarding (arXiv:2607.24410)

**Paper:** "The Fundamental Structure of Risk: From Characteristics to Covariance" — Alouadi & Lehalle (2026-07-27)

**Key findings:** Return-based covariance estimation is hostage to noisy, asset-specific time series. The **Characteristic-Driven Dynamic Factor Model (CD-DFM)** instead builds the cross-sectional representation from *observable firm characteristics* (mainly fundamentals). The latent space jointly yields interpretable factor exposures and a **forward** covariance estimator, trained end-to-end on a Stein covariance loss + factor-reconstruction term targeting out-of-sample second moments. Because the encoder depends only on characteristics, **previously unseen assets can be embedded at inference time without retraining** (zero-shot onboarding). On S&P 500 equities it delivers competitive covariance forecasts despite using substantially lower-frequency information than return-based approaches.

**Framework mapping:** Strengthens the **Fundamentals** factor (§2) and the correlation/covariance backbone shared by §13.8.3 (denoised-correlation breadth), §13.9.5 (diversification clustering) and §13.9.4 (CVaR allocation). Fixes a structural weakness: every correlation consumer in this skill currently requires a long return history per symbol, which fails on IPOs, newly listed ETFs and symbols with regime breaks.

**Signal design:** Add `characteristic_covariance(characteristics, returns=None)` to `scoring_engine.py`:
- Fit the characteristic→exposure encoder on the universe's fundamentals panel; produce forward covariance `Σ̂` **without** requiring a per-symbol return window.
- Route `Σ̂` into the same consumers as the denoised correlation matrix: breadth (§13.8.3), diversification clustering (§13.9.5), CVaR budget (§13.8.5/§13.9.4).
- **Zero-shot path** (the main practical gain): a symbol with < 60 return observations — new listing, post-restructuring, newly included index member — gets a covariance row from characteristics alone instead of being dropped or given a garbage estimate.
- Blend rule: `Σ_use = w·Σ̂_char + (1−w)·Σ_denoised_returns`, with `w → 1` as the symbol's return history shortens. Never silently fall back to a return-based estimate on a short window (that is exactly the noise the paper removes).

**Caveat:** Characteristics are **low-frequency** (quarterly fundamentals). CD-DFM is a *risk-model* upgrade, not a short-horizon signal — do not use it to time entries. Interpretability of the latent factors must be re-checked per market; the paper validates on S&P 500 only.

---

#### 13.10.2 Early-Warning Signals Are Event-Heterogeneous — Guard-Rail on §13.8.4 (arXiv:2607.27070)

**Paper:** "Where does the criticality live? Early-warning signals are event-heterogeneous across seven crypto-perpetual liquidation cascades" — Garcia Seuma (2026-07-29)

**Key findings:** Across seven major BTC liquidation cascades (2022–2025, incl. the record $19B event of 2025-10-10), rolling variance and lag-1 autocorrelation on detrended residuals were Kendall-tau tested over **39 analysis configurations per variable per event**. Result: **no variable is event-invariant.** Price carries the critical-slowing-down (CSD) signature in 5 of 7 events but is **silent in exactly the two exogenous news (tariff) shocks** — implying a two-type structure: *endogenous buildup* vs *exogenous shock* cascades. The October-2025 event, where the signature appeared to live in leverage rather than price, is the **outlier, not the rule**. The only regularity surviving all events is a **compression of taker order-flow variance** (300-onset placebo test, Fisher-combined p ≈ 5e-6) — but it is a *population-level precursor, not a per-event alarm*. Conclusion: single-event CSD claims in derivatives are **fragile by construction**; slowing-down is absent precisely where the destabilising mechanism is most abrupt.

**Framework mapping:** Directly **constrains §13.8.4** (eigenvector-rotation crisis early-warning) and §13.3 regime detection. §13.8.4 was adopted as a *leading* crisis indicator; this paper shows that any CSD-family early-warning — variance, AC(1), eigenvalue *and* eigenvector-rotation reads — is only valid for the **endogenous-buildup** cascade type and is structurally blind to exogenous shocks.

**Signal design:** Amend `covariance_early_warning()` in `scoring_engine.py`:
- Return a **typed** warning: `{'signal': bool, 'regime_type': 'endogenous'|'unknown', 'population_level': True}` — never a bare boolean alarm.
- Treat the output as a **population-level prior that tilts weights**, not a per-event trigger that flips the book. Concretely: cap its effect on `risk_scale` (e.g. max −30%) instead of allowing a full defensive switch.
- **Never** rely on early warning as the sole tail defence. The exogenous-shock branch is undetectable by construction, so the standing tail protections — `tail_risk_gate` (§13.8.5), position caps, asymmetric-vol CVaR (§13.9.4) — must remain armed **at all times**, regardless of the warning state.
- Add order-flow-variance **compression** as a secondary input where taker/aggressor flow is available (the one regularity that survived all seven events); still population-level.
- Reporting discipline: any CSD-type claim must state the number of analysis configurations swept and pass a placebo/onset test — a single tuned configuration is not evidence (feeds `audit_checklist()`, §13.9.6).

**Caveat:** Evidence base is crypto perpetuals; the *mechanism* argument (abrupt shocks cannot slow down first) generalises, the *magnitudes* do not. This subsection **removes confidence**, it does not add a factor.

---

#### 13.10.3 Shadow-Before-Swap: Forward-Gated Factor/Model Replacement (arXiv:2607.28577)

**Paper:** "Train Often, Deploy Selectively: Forward-Gated Model Replacement in Crypto Markets" — Dutta (2026-07-30)

**Key findings:** A retrained candidate does **not** necessarily beat a continuously maintained incumbent. **Shadow Before Swap (SBS)** warm-refits a challenger *off the serving path*, evaluates it against the maintained incumbent on the **same next week of delayed labels**, and promotes only after a fixed **paired negative-log-likelihood (NLL) advantage**. Over 48 UTC weeks, 3 seeds, 8 underlyings and 2 contract types, SBS cut NLL by 0.147% vs calendar replacement, 0.076% vs schedule-matched automatic promotion, and 0.043% vs continuous maintenance — while promoting only **114 of 528 challengers (−78.4% deployed model changes)**. Effect directionally consistent across seeds, trial budgets, promotion margins and an earlier 20-asset panel.

**Framework mapping:** Generalises the **retention/hysteresis rule** of §13.9.5 from *portfolio holdings* to *factors and models*, and slots into **§14 factor governance** as a deployment gate downstream of `evaluate_factor_3level` / `walk_forward_validate`. Fills a real gap: the governance chain currently decides *admit vs reject* but has no rule for *replace incumbent vs keep incumbent*.

**Signal design:** Add `shadow_before_swap(incumbent, challenger, holdout_labels, margin)` to `factor_governance.py`:
- Refit the challenger **off the serving path**; score both models on the **same forward holdout** of delayed labels (never on the challenger's own fit window).
- Promote only if `NLL(incumbent) − NLL(challenger) > margin` on a **paired** comparison (same samples, same horizon). Default `GOV_SWAP_MARGIN` conservative — the paper's value is that most challengers are correctly *not* promoted.
- Apply the identical rule to factor rotation: a candidate factor replaces an incumbent only on a paired forward-holdout advantage, not on backtest IC superiority.
- Log every non-promotion. A high promotion rate is a red flag for an under-strict margin, not a sign of a productive research pipeline.

**Caveat:** Paired NLL requires a **probabilistic** output. For point-forecast factors, substitute a paired proper score (Brier for direction, §13.9.3; pinball for quantiles). Delayed-label evaluation must respect the purge/embargo rules of §13.9.6 — the "same next week" holdout is only valid if labels are fully realised.

---

#### 13.10.4 Effective Sample Size Gate: When Outcome Records Cannot Attribute Skill (arXiv:2607.27544)

**Paper:** "Lucky or Good? Outcome Noise, Effective Sample Size, and the Attribution of Skill" — Ulrich (2026-07-30)

**Key findings:** Any decision domain is characterised by two parameters — the **noise in each outcome** and the **effective number of independent outcomes** over the observation window. Plotted in that 2-D space, the domains where capital and prestige are routinely allocated on realised outcomes — **mutual fund management, venture capital, executive performance** — fall in the region where outcome records contain **too little signal to support reliable individual-level inference**. The prescribed substitute is the population-level empirical validation used in medicine: ask whether the actor **adopted the practices** that are associated with better outcomes at the population level.

**Framework mapping:** Supplies the missing *precondition* for §13.9.2 (triple-gate admission) and §13.9.3 (calibration multiplier). Both currently ask "did it pass the test?"; this paper asks the prior question — **"does this record even have enough effective observations for the test to mean anything?"** It also formalises the existing L2 economic-logic gate of §14.2: the "practices" criterion *is* the process-based substitute when outcomes are uninformative.

**Signal design:** Add `effective_sample_gate(factor_returns, outcome_noise)` to `factor_governance.py`, executed **before** the three gates:
- Compute **ESS** with the autocorrelation correction `ESS ≈ n / (1 + 2·Σρ_k)` — overlapping windows and serially correlated factor returns inflate raw `n` badly (consistent with the no-IID rule, constraint #11).
- Compute the noise-to-signal ratio per outcome; locate the factor in the (noise, ESS) plane. If it lands in the **insufficient-signal region**, the verdict is `INSUFFICIENT_EVIDENCE` — distinct from both PASS and REFUTED, and distinct from §13.9.2's INCONCLUSIVE (which means *tested and unresolved*; this means *not testable*).
- On `INSUFFICIENT_EVIDENCE`, the outcome record is **inadmissible**. Fall back to the **process criterion**: does the factor implement a mechanism with population-level support (L2 four-dimension economic rubric, §14.2)? Admission then requires ≥ 3/4 L2 dimensions *and* a hard weight cap.
- Same test on *strategy* evaluation: a live track record with low ESS may not be used to raise leverage or to claim manager skill.

**Caveat:** ESS is itself estimated and is fragile when the ACF is poorly determined; prefer a conservative (lower) ESS. This gate **only removes false confidence** — passing it grants no edge.

---

#### 13.10.5 Coherence Projection for Probabilistic Intervals (arXiv:2607.26792)

**Paper:** "Crossing-Free Probabilistic K-Line Forecasts Without Retraining" — Yu, Tao, Chen, Wang & Bunn (2026-07-29)

**Key findings:** Probabilistic OHLC ("K-line") forecasts suffer two incoherence modes: **quantile crossing** (a higher-quantile forecast below a lower one) and **K-line crossing** (forecast low above open/close, or forecast high below open/close). Existing fixes handle only one, via output reordering, specialised architectures, or penalised training. **KQSP (K-line–Quantile Sequential Projection)** is **parameter-free and training-free**, applies to forecasts from *any* model (including pretrained foundation models), drives both crossing rates to **zero on all test data**, and does so with **substantially smaller corrections** to the original forecasts than competing methods.

**Framework mapping:** A drop-in post-processor for **§13.7 UQ** (`conformal_halfwidth`, `bootstrap_ci`) and **§13.6** volatility prediction intervals. Relevant to this skill because interval outputs already feed sizing: `ci_low`/`ci_high` drive `position_confidence`, and an incoherent interval silently corrupts the multiplier.

**Signal design:** Add `project_coherent_intervals(quantiles, ohlc=None)` to `uncertainty_quantification.py`:
- Sequential projection onto the coherence constraint set: (a) monotone quantiles `q_τ1 ≤ q_τ2` for `τ1 < τ2`; (b) OHLC ordering `low ≤ min(open, close) ≤ max(open, close) ≤ high`; (c) `ci_low ≤ point ≤ ci_high` for every scalar signal interval.
- **Training-free and model-agnostic** — run it as the last step on *any* interval, whether from moving-block bootstrap, split conformal, Log-HAR+TTM (§13.6) or an external TSFM.
- Additional constraint for this skill: forecast **RV must be non-negative**, so project the volatility interval onto `[0, ∞)` before percentile scoring.
- Log the projection magnitude. A large correction means the upstream forecaster is badly miscalibrated — feed that into the Brier/Winkler calibration multiplier (§13.9.3) rather than quietly repairing it.

**Caveat:** Projection enforces *coherence*, not *coverage*. A crossing-free interval can still undercover; conformal calibration (§13.7) remains mandatory. Apply projection **after** calibration, never as a substitute.

---

#### 13.10.6 Passive Market Impact: Limit-Order Fills Are Not Free (arXiv:2607.28323)

**Paper:** "Optimal Execution with Passive Market Impact" — Barzykin, Boyce, Neuman & Tuschmann (2026-07-30)

**Key findings:** A mesoscopic optimal-execution model built on two empirical observables: (1) limit-order **fill probability decays approximately exponentially** with distance from the midprice, and (2) price changes respond **linearly, short-term, to order-flow imbalance**. Combining them yields a reduced-form **passive impact rate that decays exponentially with quote distance**. Passive execution therefore trades off higher fill intensity + larger accumulated impact against lower impact + greater **non-execution risk**, together with adverse selection and opportunity cost. Calibrated on NASDAQ equities and public FX; extensions cover heterogeneous decay rates, transient impact and target schedules.

**Framework mapping:** Extends **§13.1** (square-root law, aggressive impact) and **§13.2** (dynamic commission/slippage) to the **passive** side, which both currently treat as free. Also hardens `audit_checklist()` (§13.9.6): a backtest assuming limit orders fill at the quoted price with zero impact is optimistic in two independent directions at once.

**Signal design:** Extend `_calculate_dynamic_slippage()` in `simulated_broker.py` with a passive branch:
- Model fill probability as `p_fill ≈ exp(−δ/κ)` in quote distance `δ` from mid (calibrate `κ` per symbol from realised fill data; default from the symbol's spread and volatility).
- Charge a **passive impact** term that decays exponentially in `δ` — do **not** book passive fills at zero cost.
- Book **non-execution risk** explicitly: with probability `1 − p_fill` the order does not fill, and the backtest must either miss the trade or cross the spread later. Both outcomes must be recorded; silently assuming a fill is look-ahead.
- Add to `audit_checklist()`: *"Passive/limit-order fills are modelled with a fill probability and a non-zero passive impact; unfilled orders are accounted for."* Unchecked ⇒ UNRELIABLE.
- Practical read for the 4-Layer framework: the **high-fee-rate veto** (−10) understates true cost for passive strategies. Include expected passive impact + non-execution cost in the fee-rate estimate before evaluating the veto.

**Caveat:** Calibration needs order-level fill data, unavailable in most retail daily feeds. Default to a conservative parametric `κ`; the actionable takeaway without microstructure data is simply **stop assuming free passive fills**.

---

#### 13.10.7 A-Share Herding Crowding Read + Market-Aligned Sentiment (arXiv:2607.27063, arXiv:2607.28127)

**Papers:** "Herding, Momentum, and Reversal in China's A-Share Market: An Agent-Based Network Model with Information Diffusion" — Weng (2026-07-29); "FinSMART: Financial Sentiment Analysis for Algorithmic Trading through Market-Aligned Reinforcement Learning" — Iacovides, Zhou & Mandic (2026-07-30)

**Key findings (2607.27063):** An agent-based model on lattice and network topologies (von Neumann/Moore, Erdős–Rényi, Watts–Strogatz) shows that **local herding + delayed information diffusion jointly generate momentum and its subsequent reversal**. Stronger herding ⇒ spatially clustered trading, larger price fluctuations, higher **excess kurtosis**. Faster diffusion shortens convergence to the signal-implied value, but *diffusion + social reinforcement together produce overshooting and reversal*. Empirically on A-shares: conventional **CSAD** and **LSV** herding measures are compared with a **rolling tail-based herding indicator (after Johnson SU transformation)**; all display similar time variation and **rise during major market disruptions**. Momentum and reversal are attributed to information delay, local reinforcement, and the eventual **decay of herding**.

**Key findings (2607.28127):** Existing financial-sentiment LLMs are **market-agnostic** — supervised on static, human-annotated data, unable to adapt as conditions change. FinSMART is a **market-aligned RL** framework that optimises sentiment signals directly against **realised market outcomes**, using market-aware data filtering plus a discrete **asymmetric** trading reward for stability under noisy, non-stationary, multifactorial data. Reported +220% cumulative return over the strongest baseline, and it supports **market-aware retraining at any time** by substituting newly observed articles + realised outcomes for manual annotation.

**Framework mapping:** (a) 2607.27063 adds an **A-share crowding factor** to §2 sector/breadth and a **momentum-exhaustion condition** to §13.9.1 trend-quality — the skill's momentum block has no crowding-decay read today. (b) 2607.28127 upgrades §13.8.6 news sentiment from static supervised scoring to market-aligned, retrainable scoring, and pairs with §13.10.3 for *when* to promote a retrained sentiment model.

**Signal design:**
- Add `herding_indicator(cross_section_returns, method="tail_johnson_su")` to `scoring_engine.py`: compute CSAD, LSV, and the rolling tail-based measure after Johnson SU transformation; report all three and flag divergence (the paper finds them concordant — divergence is a data-quality alarm).
- **Regime input:** rising herding ⇒ crowding buildup. Feed into `_detect_regime()` alongside denoised breadth (§13.8.3); herding spikes coincide with major disruptions, so it is a **coincident stress read**, deliberately *not* claimed as leading (consistent with §13.10.2's warning against fragile early-warning claims).
- **Momentum-exhaustion condition:** high herding + decaying herding slope + price extended vs signal-implied value ⇒ elevated **reversal** risk. Apply as a soft veto on fresh momentum entries (shrink `risk_scale`), **not** as a short signal.
- **Fat-tail linkage:** stronger herding predicts higher excess kurtosis ⇒ raise the CVaR loss-budget requirement in `tail_risk_gate` (§13.8.5) when the herding indicator is elevated.
- **Sentiment upgrade:** make `news_sentiment_score()` pluggable with a market-aligned backend — train/refresh the sentiment scorer against realised forward returns with an asymmetric reward, rather than static annotation labels. Promote any refreshed sentiment model only through `shadow_before_swap` (§13.10.3).

**Caveat:** The A-share herding evidence is model-plus-indicator, not a validated tradable factor — admit only through the ESS gate (§13.10.4) and triple-gate (§13.9.2). FinSMART's +220% headline is a single-paper backtest claim: it must clear `audit_checklist()` (§13.9.6) before its sizing is trusted, and market-aligned RL optimised on realised outcomes has an **elevated overfitting surface** precisely because it trains on the target. Keep the sentiment weight small (§13.8.6 caveat: low-frequency overlay, ~5% of the fundamentals bucket).

---

### 13.11 This-Week arXiv Integration (2026-08-04 ~ 2026-08-10)

Crawled the arXiv **q-fin** recent listing (announcements 2026-08-04 → 2026-08-10, **92 papers** incl. cross-lists); scanned all titles, read 8 abstracts, and selected 8 papers grouped into 7 subsections with a direct, non-speculative mapping. Follows the opt-in, config-driven, graceful-fallback pattern of §13.6–§13.10.

This week's theme is **uncertainty → sizing, co-movement → structure, sharp → robust**, with a strong *evidence-discipline* throughline. Three of the eight papers are as much about **how not to fool yourself** as about new alpha: Conformal Kelly's development-window edge collapsed out-of-sample under pre-registration (§13.11.1); a QLoRA LLM sentiment benchmark shows classification accuracy does **not** survive as tradable IC (§13.11.6); and a Shapley forecast-gap attribution supplies the missing "why did the number change" decomposition for shadow-before-swap (§13.11.5).

#### 13.11.1 Conformal Kelly: Interval-Width Position Sizing + an Honest OOS Collapse (arXiv:2608.01494)

**Finding:** Reuse a 75% conformal interval (from the §13.7 / `uncertainty_quantification` module) as the **scale** in fractional Kelly — wider interval ⇒ shrink the position, narrower ⇒ grow it. Counter-intuitive robustness result: when an interval **sizes** a position rather than describing a forecast, **width stability beats local sharpness** — the winner was the *simplest* slow, unweighted, per-asset rolling quantile; every faster-adapting tweak cost 0.7–5.3 pts of annual growth, and it beat textbook std-dev sizing by 2.1 pts at matched leverage. A downside-breach de-lever (cut leverage when intervals miss low far above their historical rate) cut max DD 27.7%→20.3% while raising Sharpe, beating all 40 placebo timings (p = 1/41). **But**: the 28.5% development-window CAGR came from an autonomous 200-config LLM-agent search; after sealing 2022+ data and pre-registering, the two chosen configs earned only 8.5% / 7.0% — **below passive benchmarks** — even though calibration held (0.745 vs 0.750 nominal).

**Framework mapping:** Directly connects the **uncertainty-quantification module** (§13.7 conformal half-width `ci_low`/`ci_high`) to **position sizing** (§5) and `risk_scale`. Fills a gap: the skill already computes conformal intervals and a linear `risk_scale`, but has no principled interval-width → Kelly-fraction map nor a downside-breach de-lever rule.

- `conformal_kelly_scale(point, ci_low, ci_high, kelly_fraction)`: map interval **width** to a fractional-Kelly multiplier; **default to slow, unweighted, per-asset rolling quantiles** (do not adaptively reweight for speed — width stability is the design goal). Run through coherence projection (#34) and calibration (§13.9.3) **before** sizing.
- Downside-breach de-lever: track rolling downside coverage; when realized downside misses exceed the nominal rate by a margin, tighten the `risk_scale` floor (a leverage cut, **not** a directional/short signal).
- Config-driven, default off (`ENABLE_CONFORMAL_KELLY=False`); `kelly_fraction ≤ 0.5`.

**Caveat (evidence discipline, feeds §13.9.6 / §13.10.4):** the paper is itself a cautionary tale — a 200-config agentic search produced a development edge that **did not survive pre-registered OOS**. Any Conformal-Kelly config must be sealed / pre-registered and clear `audit_checklist()` (#25) + the ESS gate (#33) before its sizing is trusted; *calibration holding is not evidence of growth*. Keep all standing tail protections (#31) armed.

#### 13.11.2 MINGLE: Locality by Factor Exposures, Not Co-Movement (arXiv:2608.06618)

**Finding:** MINGLE jointly learns a latent factor representation and its induced graph topology via a unified ADMM, redefining graph **locality** through **systematic factor-exposure similarity** rather than observed co-movement. The exposure-similarity graph aligns more closely with established economic sectors than correlation-based graphs; portfolios built on it consistently beat correlation-based counterparts across volatility regimes and transaction-cost levels (confirmed by paired statistical testing).

**Framework mapping:** Upgrades the correlation/covariance backbone shared by §13.8.3 (denoised-correlation breadth), §13.9.5 (TDA diversification clustering), §13.10.1 (CD-DFM covariance) and §2 sector. All of these currently derive structure from *observed return co-movement*; MINGLE groups by *why* assets move together (shared exposures), which is more stable and sector-aligned.

- `exposure_similarity_graph(returns, factor_loadings)`: build the breadth/clustering graph from exposure profiles, not raw correlation; feed the sector-aligned graph into breadth (§13.8.3), diversification clustering (§13.9.5) and the covariance consumers (§13.10.1 / §13.9.4).
- Graceful fallback: when factor loadings are unavailable (IPOs, short history), fall back to the denoised-correlation graph (§13.8.3) / CD-DFM zero-shot covariance (§13.10.1).
- Config-driven, default off.

**Caveat:** MINGLE requires a credible factor model; a mis-specified exposure set yields a confidently wrong graph. Treat exposure-graph vs correlation-graph disagreement as a **data-quality flag**, and keep single-name / sector caps (#30) armed regardless of which graph is used.

#### 13.11.3 Drawdown Beyond Brownian: Non-Gaussian, Long-Memory Drawdown Calibration (arXiv:2608.00127)

**Finding:** Extends the Rej–Seager–Bouchaud drawdown framework as a transparent Monte-Carlo experiment mapping Sharpe + return structure to four decision measures — **max drawdown, max loss, longest negative time, longest recovery time**. Relaxing Gaussianity (skew, fat tails, vol clustering, Sharpe-estimation uncertainty) moves the four measures *differently* — a single Gaussian table mis-warns. Under fractional Brownian motion, the apparent persistence-driven amplification of *max-DD depth* is almost entirely self-similar dispersion scaling **T^(H−1/2)** — a **square-root-of-time calibration failure**, not intrinsic path danger.

**Framework mapping:** Upgrades §13.8.5 `tail_risk_gate` and drawdown expectations, and continues the standing "no-IID / no-Gaussian" rule (#11 / #17). Also refines §13.10.2: don't over-attribute danger to persistence — correct the time-scaling first.

- `drawdown_budget(sharpe, return_stats, horizon)`: return expected {maxDD, maxLoss, negTime, recoveryTime} from a Monte-Carlo lookup **calibrated to the strategy's own skew / kurtosis / vol-clustering**, not a Gaussian closed form; use it to set drawdown alarms and de-lever thresholds.
- Long-memory correction: scale DD-depth expectations by T^(H−1/2) rather than √T when H≠0.5; **label the difference as calibration, not new risk**.
- Config-driven, default off; fall back to the Gaussian table with an explicit "mis-warn risk" log when higher moments can't be estimated.

**Caveat:** the four measures must be budgeted **separately** — a strategy can be fine on max-DD depth yet fail on recovery time. Report all four; never collapse to a single drawdown number.

#### 13.11.4 Certified Wasserstein Distributionally-Robust Allocation (arXiv:2608.07032)

**Finding:** A **certified**, scalable approximation for high-dimensional Wasserstein DRO portfolio optimization. For long-only box-support portfolios under the one-norm ground metric, the robust expected-utility problem reduces to a **polynomial-size linear program** (hyperplane majorization + support dualization); the uniform utility-approximation error **bounds both the robust-value error and the near-optimality gap**. Demonstrated on 476-asset monthly rebalancing, scalable to 1,000 assets.

**Framework mapping:** Upgrades §5 allocation and §13.9.4 CVaR allocation with a *worst-case-robust* weight solver carrying an explicit **certificate** — a stronger guarantee than point-estimate mean-variance / CVaR. Pairs naturally with §13.11.2 / §13.10.1 covariance inputs.

- `wasserstein_robust_weights(mu, support_box, radius, utility)`: solve the finite hyperplane-dual LP over polyhedral constraints; expose the approximation-error bound as the allocation's **certificate** and log it.
- Set the Wasserstein radius from estimation uncertainty (link to ESS #33 — smaller effective sample ⇒ larger ambiguity radius).
- Config-driven, default off; fall back to CVaR / mean-variance when the LP is infeasible or the asset count is small.

**Caveat:** robustness is not free — an over-large radius yields overly conservative, near-equal-weight portfolios. Tune the radius by OOS performance under `audit_checklist()`, and keep single-name / sector caps (#30).

#### 13.11.5 Forecast-Gap Attribution as a Cooperative Game (arXiv:2608.04547)

**Finding:** When a forecast changes run-to-run, decompose the total change into per-input contributions (portfolio data, macro scenario, model spec, business assumptions, management overlays) as a **cooperative game** — exact Shapley, nested/hierarchical Shapley, Integrated Gradients, Gradient/Permutation/Kernel SHAP — with an allocation that **reconciles to the total** without an arbitrary sequence of input replacements. The paper compares allocation rules, cost, and governance suitability (CCAR / CECL context).

**Framework mapping:** Fills a real gap in **§14 governance** and **§13.10.3 shadow-before-swap**. Today the governance chain decides admit/replace but has **no principled decomposition of why a challenger's or incumbent's forecast moved**. Forecast-gap attribution answers "which input drove the delta," which is exactly what a shadow-before-swap decision and a §13.10.4 skill-attribution audit require.

- `attribute_forecast_gap(inputs_run_a, inputs_run_b, model)`: return an additive, total-reconciling attribution over inputs; default to **nested Shapley** for hierarchical input groups, fall back to Kernel SHAP when exact Shapley is infeasible (record which estimator was used).
- Wire into `shadow_before_swap` (#32): before promoting a challenger, report the attribution of its edge to inputs vs model change; an edge driven purely by a single volatile input is a **demotion flag**.
- Config-driven, default off.

**Caveat:** attribution explains a change, it does **not** validate it — a large "model-spec" contribution is not evidence the model is better; it still must clear the triple gate (#27) and ESS gate (#33). Approximate SHAP estimators need not reconcile exactly; use exact/nested Shapley only when reconciliation to the total is required for governance sign-off.

#### 13.11.6 Sentiment Classification ≠ Return Predictability — Guard on §13.8.6 / §13.10.7 (arXiv:2608.04200)

**Finding:** A unified QLoRA benchmark separates linguistic performance from economic value. Mistral-7B tops classification (acc 0.884, macro-F1 0.877) and QLoRA lifts Qwen2.5's macro-F1 from 0.727→0.862 — **but** on a temporally separate 2019 sample (10,637 headlines, S&P100), all seven downstream models give only small positive one-day rank IC (largest **0.0143**, FinBERT), and **none of the 28 model-horizon tests survive Newey–West + FDR**; portfolio results show no robust advantage.

**Framework mapping:** A rigorous guard-rail on the §13.8.6 news-sentiment factor and the §13.10.7 market-aligned upgrade. It mandates: do **not** size a sentiment factor by its classification accuracy; require forward-return IC that survives multiple-testing correction with HAC / Newey–West inference.

- Harden `news_sentiment_score()` admission: gate on **forward-return rank IC significant after Newey–West + BH-FDR**, not classification F1 (feeds triple gate #27 and audit #25). QLoRA is confirmed effective for *adaptation*, so keep it as the encoder — just don't trust its labels as alpha.
- Enforce the existing small-weight cap (#18, ~5% of the fundamentals bucket) until the IC clears correction; if it never does, the factor stays a soft confirmation overlay, never a sizer.

**Caveat:** consistent with §13.10.7's warning that market-aligned RL sentiment has an elevated overfitting surface. Classification benchmarks are necessary but not sufficient; the burden of proof is **tradable, multiple-testing-robust IC**.

#### 13.11.7 Cross-Sectional Heterogeneity: Sector Embeddings + Informed-Flow Persistence (arXiv:2608.05755, arXiv:2608.04373)

**(a) Sector embeddings (2608.05755):** An LSTM augmented with **learnable sector embeddings + macro covariates** beats a plain LSTM, Random Forest and buy-and-hold on a cross-sectional S&P500 long-short; the predictive signal decomposes into a **short-term reversal factor + an industry-momentum factor**, and a weight-based contribution metric quantifies sector influence. Confirms that a single one-size-fits-all cross-sectional model is mis-specified — heterogeneity must be modeled explicitly.

**(b) Informed-flow persistence (2608.04373):** On a fully public-identity DEX order book (17.1B messages, 147k wallets), **informativeness is a persistent per-wallet attribute** (10-day rank corr 0.52); adding top-ranked wallets' live activity to an anonymous benchmark raises 1-second OOS R² by 13.2% (t = 9.2), 1.6× the best of 200 placebo cohorts.

**Framework mapping:** (a) Strengthens §2 **sector** (heterogeneous, sector-aware treatment rather than pooled scoring — aligns with §13.11.2's exposure grouping), reinforces the §13.9.1 **industry-momentum** read, and legitimizes a **short-term reversal** factor. (b) Supplies an informed-flow read for §2 volume/fund-flow — its A-share analog is **龙虎榜 (LHB) seat-level informativeness persistence**: rank broker/seat identities by post-print price impact and treat persistently informed seats as a fund-flow confirmation.

- Sector-aware scoring: allow per-sector factor treatment (learnable/embedded sector adjustment or, minimally, sector-conditional normalization); add a short-term-reversal sub-factor alongside industry momentum, both admitted through the triple gate (#27) and ESS gate (#33).
- Informed-flow (A-share): `informed_seat_score()` — rank LHB seats by persistence of post-appearance forward returns over adjacent windows; use persistent-informed-seat activity as a small fund-flow confirmation, **never** a standalone sizer.
- Config-driven, default off.

**Caveat:** (a) sector embeddings risk overfitting on short histories — regularize and validate OOS. (b) The public-wallet mechanism does **not** transfer directly to A-shares (no per-order public identity); the LHB-seat analog is delayed (T+1 disclosure), coarse (seat-level, not order-level) and gameable — admit only through the ESS gate (#33) and treat as a coincident / short-horizon confirmation, **not** a leading signal (consistent with #31).

---

## Usage Examples

**Example 1: Build a multi-factor scoring system for A-shares**

User: "帮我构建一个A股多因子评分系统，包含动量、技术指标、成交量、基本面、宏观经济、行业板块六个维度"

To complete this task:
1. Create the file structure (data_loader.py, scoring_engine.py, etc.)
2. Implement data loading for A-shares using `akshare`
3. Calculate factor scores with equal weights (16.7% each)
4. Generate trading signals using dynamic thresholds
5. Run backtest and visualize results

**Example 2: Optimize factor weights**

User: "帮我优化多因子模型的权重，动量因子的重要性更高"

To complete this task:
1. Run parameter optimization (`optimization.py`) to find best weights
2. Use grid search or Bayesian optimization
3. Evaluate performance with different weight combinations
4. Update `config.py` with optimized weights

**Example 3: Run simulated trading**

User: "帮我运行模拟交易，初始资金10万，交易A股和港股"

To complete this task:
1. Initialize `SimulatedBroker` with 100,000 capital
2. Load data for A-shares and HK stocks
3. Calculate scores and generate signals
4. Execute trades according to signals
5. Track portfolio performance and generate report

## Notes

- **Data Quality:** Ensure data quality before calculating scores. Handle missing data, adjust for stock splits and dividends.
- **Survivorship Bias:** Include delisted stocks in backtests to avoid survivorship bias.
- **Transaction Costs:** Account for commissions, slippage, and market impact in backtests.
- **Overfitting:** Avoid over-optimizing factor weights. Use out-of-sample testing.
- **Regime Changes:** Factor performance varies across market regimes. Consider regime-dependent weights.

## Troubleshooting

**No trading signals generated:**
- Check if factor weights sum to 1.0
- Lower buy threshold percentile (e.g., from 80 to 70)
- Verify data quality and indicator calculations

**Poor backtest performance:**
- Review factor definitions and calculations
- Check for data snooping bias
- Validate with out-of-sample testing
- Consider transaction costs and slippage

**Data loading fails:**
- Verify symbol formats (A-shares: `600519.SH`, HK: `0700.HK`, US: `AAPL`)
- Check internet connection for `akshare` and `yfinance`
- Use local data cache to avoid repeated downloads

## References

For detailed implementation of each module, refer to the code files created in the user's project directory. Each file contains detailed comments and examples.

**External References:**
- `akshare` documentation: https://akshare.akfamily.xyz/
- `yfinance` documentation: https://pypi.org/project/yfinance/
- `ta` library documentation: https://technical-analysis-library-in-python.readthedocs.io/

---

### 13.12 This-Week arXiv Integration (2026-08-10 ~ 2026-08-16)

> 本周扫描 arXiv q-fin 公告（2026-08-10~08-14 的 daily archive + new listing，约 120 篇标题，含摘要精读 35 篇），筛 8 篇映射到技能模块，1 篇作护栏落位。本周主题：**波动率集成回归（regime 路由 + 部署期校准）**、**信号解耦（alpha/beta 触发 + 认知不确定性收缩）**、**回测可取性证明**、**结构网络（部门间失衡 / 下谱同步 / 事件驱动波动）**、**准入边界（分类边界邻近）**。全部遵循 opt-in / config-driven / graceful-fallback 范式：仅文档化函数签名与准入条件，不写投机性新 `.py`。

#### §13.12.1 Regime-Gated Volatility Routing (arXiv:2608.12251)
- **论文**：Regime-Gated Residual Mixture-of-Experts for Cross-Sectional Volatility Forecasting（q-fin.ST，2026-08-12）。5 日实现波动率预测，1027 支美股 walk-forward。
- **核心发现**：将 regime 状态**仅用于专家路由**（gating），**不**作为预测输入直接拼接；直接拼接 regime 反而同时损害预测精度与训练稳定性；soft routing 稳定优于 hard routing。
- **Framework mapping**：升级 §5 `volatility_forecaster` 与 §13.3 regime 接入方式——regime 信息应通过路由门控影响残差修正，而非作为特征进入主干。与 #16（regime 领先指标）互补。
- **信号设计**（opt-in）：
  - `regime_routed_vol_correction(base_pred, regime_state) -> residual_correction`：regime 状态变量仅输入 gating network；base predictor 不含 regime 特征；soft routing（`softmax` 权重），默认关闭 hard routing。
  - 优雅回退：无 regime 状态（初创/短史标的）→ 退化为容量匹配的 plain MLP（§5 基础路径），不报错。
  - 验证：walk-forward 滚动评估，RG-ResMoE 须在 VaR 校准误差上优于容量匹配 MLP 方可启用（过 #25 审计）。

#### §13.12.2 Calibration-Period-Aware Deployment Gate (arXiv:2608.12259)
- **论文**：Calibration Bets on the Past: Post-Training Quantization for Financial Time-Series Forecasting（cs.LG，2026-08-12）。跨截面波动率预测 PTQ 系统研究，7 架构 × 8 walk-forward 年 × 560 模型。
- **核心发现**：4-bit 激活量化下，校准方式成为预测性能首要决定因素——默认 abs-max 静态校准抹掉 11–62% 全精度 IC；改用 **percentile 校准**可恢复 53–94%；且**优选激活范围随市场状态变化**——窄范围在常态市提升分辨率，但当测试期市场离散度超过校准历史时优势丧失。
- **Framework mapping**：强化 §15.1 实时成本标定 / 部署纪律层——量化部署的激活校准窗口必须覆盖当前市场离散度 regime，否则退化为更稳健配置。延续 #33 ESS / #35 范围边界精神。
- **信号设计**（opt-in）：
  - `calibration_coverage_gate(live_dispersion, calib_dispersion_window) -> {'PASS','DEGRADE','FALLBACK_8BIT'}`：计算当前市场离散度相对校准窗口的分位；> 上尾阈值 → `DEGRADE`（缩窄量化位宽收益预期）/ 远超 → `FALLBACK_8BIT`（或 weight-only 4-bit）；默认 8-bit 激活或 weight-only 4-bit 为稳健 fallback。
  - 优雅回退：无实盘/历史校准数据 → 保留全精度或 8-bit，记日志，不强制 4-bit。
  - 验证：每条部署 path 记录校准窗口覆盖度，纳入 `audit_checklist()`（#25）。

#### §13.12.3 Disentangled Alpha/Beta Triggers + Epistemic Covariance Shrinkage (arXiv:2608.12283)
- **论文**：Large Language Model-Driven Small-Capitalization Trading: Integrating Financial News Sentiment, Macroeconomic Indicators, and Technical Signals（q-fin.PM，2026-08-12）。Russell 2000，不确定性感知（aleatoric + epistemic 分解）注入协方差。
- **核心发现**：将模型风险分解为**认知（epistemic）/ 偶然（aleatoric）**两类并直接注入配置协方差（而非仅调收益）；三种选股机制——pure-alpha（宏观未解释的个股异动）、pure-beta（个股异动前宏观/行业已动）、beta 交集；**分离的独立 alpha/beta 腿通常优于要求两者同时触发的交集**；最强保守组合为 pure-beta + GPT-4o-mini 情绪 + Student-t 目标 + 40 日持有 + 风险平价（Sharpe 2.33 @100bps）。
- **Framework mapping**：升级 §2 另类数据（新闻情绪）+ §13.11.6 情绪护栏（"分类≠收益"）。本文明示——**信号触发应解耦为 OR 而非 AND**，与 #43（情绪须过前瞻 IC 校正）一致；epistemic 不确定性 → 协方差收缩（呼应 §13.7 UQ）。
- **信号设计**（opt-in）：
  - `alpha_trigger(stock_features, macro_features) -> bool`：个股异动不被宏观因子解释时触发。
  - `beta_trigger(stock_features, macro_features) -> bool`：宏观/行业指标先于个股异动时触发。
  - `epistemic_shrinkage(cov, epistemic_var) -> cov_shrunk`：以 epistemic 不确定性缩放协方差，降低高不确定标的的配置权重。
  - 组合默认 `alpha_trigger OR beta_trigger`（非 AND）；情绪编码器保留为软确认，权重受 #18 上限约束。
  - 优雅回退：无宏观数据 → 退化为 pure-alpha 单腿；情绪模型未过 IC 校正（#43）→ 仅作软确认。

#### §13.12.4 Specification-Satisfaction Backtest Verification (arXiv:2608.10410)
- **论文**：Objective-oriented quantitative investment: A specification-driven framework for automated synthesis of trading strategy pipelines（q-fin.PM，2026-08-11）。OOQI：投资者意图形式化为可证伪条款，编译器验证逐条满足。
- **核心发现**：结果导向（result-oriented）选股常在高信息比但同时仅满足 25% 规范；规范导向满足 100% 规范但仅 5.5% 分数代价。因大装配空间搜索会**膨胀表观满足率**，须将满足率本身视为统计量，对**搜索宽度、时间留痕（temporal holdout）、随机装配零模型**做 deflation。
- **Framework mapping**：强化 §14 因子治理 / §13.9.6 `audit_checklist()`——把"in-sample 成功"视为需 deflation 的统计对象，新增规范满足度检验。与 #25 审计一致。
- **信号设计**（opt-in）：
  - `spec_satisfaction_test(pipeline, spec_clauses, search_width, temporal_holdout) -> {'satisfied':bool, 'deflated_rate':float, 'null_p':float}`：对每条可证伪规范条款逐条验证；表观满足率须经搜索宽度 deflation + 时间留痕 + 随机装配零模型校正；`null_p` 不显著（即优于随机装配）方可采信。
  - 接入 `audit_checklist()`：任何经大量组件搜索得到的策略，须报告 `deflated_rate` 与 `null_p`。
  - 优雅回退：无规范条款 → 退化为既有 IC/稳定性检验。

#### §13.12.5 Inter-Sectoral Imbalance Monitor (arXiv:2608.12023)
- **论文**：Sectoral inter-dependencies drive the loss of structural balance in signed financial networks（physics.soc-ph，2026-08-12）。S&P 500 符号相关网络，结构平衡极化分解。
- **核心发现**：系统性风险期，结构失衡**主要源于行业间（inter-sectoral）交互而非行业内（intra-sectoral）**；全球极化可 regression 解释为宏观变量（供应链中断 + 通胀不确定性）。
- **Framework mapping**：升级 §2 板块轮动 / §13.11.7 板块嵌入横截面异质性——新增**行业间失衡**读数作为系统性风险状态。与 #39 暴露图结构互补。
- **信号设计**（opt-in）：
  - `intersectoral_imbalance_index(corr_matrix, sector_labels) -> {'index':float, 'intra':float, 'inter':float}`：将相关矩阵分解为符号网络，按 triadic motif 极化度量，分离 intra/inter 分量；`inter` 分量上升超阈值 → 系统性风险告警（收紧否决项、降 `risk_scale`）。
  - 优雅回退：无板块标签（单标的）→ 退化为全局极化/吸收比；仅作监控状态，不作方向信号。

#### §13.12.6 Lower-Spectrum Synchronization Factor (arXiv:2608.09641)
- **论文**：Lower spectrum of financial correlation matrices: a new perspective on market synchronization（q-fin.ST，2026-08-10）。相关矩阵**最小特征值**含市场同步信息。
- **核心发现**：经典 PCA/RMT 只看最大特征值（主导市场因子）；最小特征值同样携带有效市场结构信息，在描述性与**预测性**设定下均验证有效。
- **Framework mapping**：升级 §13.8.3 去噪相关 / §2 市场广度——新增**下谱同步因子**作为广度/同步的补充读数。与 #39 结构建图呼应。
- **信号设计**（opt-in）：
  - `lower_spectrum_sync_factor(corr_matrix, k=min_eig_count) -> float`：取相关矩阵最小 k 个特征值聚合（如均值/轨迹）；作为市场同步/分散度反向读数（下谱越低 → 同步越高/分散越差）。
  - 优雅回退：相关矩阵退化（标的过少）→ 回退上谱 PCA 主导因子；下谱仅作辅助确认。

#### §13.12.7 FOMC Pre-Announcement Volatility Gate (arXiv:2608.10693)
- **论文**：When the Fed Speaks: Dynamics and Forecasts of the Volatility Surface（q-fin.ST，2026-08-11）。IV 曲面在 FOMC 预定会议前的预公告效应。
- **核心发现**：IV 在公告前上升，短期限 OTM 期权、高波动 regime 下更显著；ML（CNN-2D-LSTM）可学习预公告不确定性，但直接对 IV 曲面建模受噪声限制。
- **Framework mapping**：升级 §5 波动率预测 + §13.10.2 事件异质性护栏——新增**事件日历驱动的波动预公告闸门**。与 #16 regime 领先指标协同。
- **信号设计**（opt-in）：
  - `fomc_preevent_gate(calendar, today, vol_surface) -> {'window':bool, 'elevated_uncertainty':bool}`：距 FOMC 会议 N 日（默认 1–2 日）内 → `window=True`，收窄 sizer、抬升 `risk_scale`；结合 IV 曲面预公告抬升确认 `elevated_uncertainty`。
  - 优雅回退：无 IV 曲面数据 → 仅用日历窗口；非美股/无 FOMC 标的 → 退化为通用事件日历闸门（财报/央行）。

#### §13.12.8 Classification-Boundary Proximity Monitor (arXiv:2608.12634)
- **论文**：The Price of Permission: Classification Uncertainty in Constrained Capital Markets（q-fin.ST，2026-08-12）。受限资本市场（如 Shariah 合规筛选）的**分类不确定性**→ 允许投资者基数（permitted investor mass）。
- **核心发现**：二元合格标签不指示可行投资者基数是否碎片化或临近变更；规则分歧 + 距边界邻近度可排序下月筛选隐含转换。证据支持将**分类风险作为组合监控状态**（非无条件溢价）。
- **Framework mapping**：升级 §2 基本面筛选 / 准入——A 股类比：ST 状态、指数调整（调入/调出）、沪股通/深股通标的变动等"分类边界邻近"作为**监控状态**而非可交易 alpha。呼应 #43 准入纪律。
- **信号设计**（opt-in）：
  - `eligibility_proximity_monitor(stock, rulebooks, boundary_dist) -> {'proximity':float, 'disagreement':float, 'state':'MONITOR'}`：当标的 eligibility 临近规则边界或多家规则书分歧时 → 标记 `MONITOR` 状态（非交易信号）；仅触发组合层监控（如降低集中度、准备再分类）。
  - 优雅回退：无多规则书 → 仅用单一边界距离；仅作监控，绝不作 sizer 或方向信号。

> **Guard / 负结果落位（呼应证据纪律）**：
> - **Triadic Stress Index（arXiv:2608.10788）**：TSI 对相关性网络的 per-node 集中度分解（diag(A³)）优于吸收比，OOS F1 +0.273；但 **lead-lag 峰值在零滞后——这是同步（coincident）状态指数，非前瞻预测**。落位为**实时集中度监控 + per-node 归因**（与 §13.12.5 网络失衡监控并列），**明确禁止**当作领先信号使用。
> - §13.12.3 / §13.12.8 的信号均定义为**监控状态或软确认**，非直接 sizer/方向信号，避免越过 #43 / #18 护栏。

---

# S_appendix：技能附录

> **重要提示**：本附录包含使用 multi-factor-scoring 技能时的关键约束和常见失误。使用 4 层评分框架（萌芽/量价/结构/确认）时，必须严格遵守以下规则。

## 【必须执行】关键步骤

### 选择评分框架时
- [ ] 明确告知用户两种框架的差异：6-Category（股票因子选股）vs 4-Layer（趋势萌芽/期货/衍生品）
- [ ] 当用户提到 OI、ATR 百分位、OBV、CMF、Supertrend、HMA、Donchian、否决项时，切换为 4-Layer Framework
- [ ] 当用户仅提到动量、技术指标、成交量、基本面、宏观、行业时，使用 6-Category Framework

### 实现 4 层评分框架时
- [ ] 在 `scoring_engine.py` 中实现 `calculate_4layer_score()` 方法，返回 L1-L4 各层子分数和否决项明细
- [ ] 每个 L1-L4 因子必须标准化到 0-100 后再按层权重加权
- [ ] 检查否决项条件，并从原始分中扣除（最终分 ≥ 0）
- [ ] 如果 OI 数据不可用，将 L1 的 `oi_change_rate` 替换为成交量 5 日增长率或换手率变化
- [ ] 生成信号前验证总分分布：买入/卖出阈值可基于最终得分分布或固定 70/30

### 构建文件时
- [ ] 创建 `scoring_engine.py` 并包含 `MultiFactorScorer` 类（支持 `framework="4-layer"`）
- [ ] 创建 `signal_generator.py` 并处理 4-Layer 框架的 70/30 阈值和否决项
- [ ] 创建 `config.py` 并提供 `LAYER_WEIGHTS`、`SPROUT_FACTORS`、`VETO_RULES` 配置
- [ ] 创建 `backtest.py` 并正确应用否决项扣分后的最终分数

## 【常见失误】执行失误警示

### ❌ 失误1：在股票上直接使用 OI 变化率
**后果**：A 股股票没有 OI 数据，导致计算失败或 NaN 分数
**修正**：无 OI 数据时自动回退到成交量增长率或换手率变化
**验证**：在 `config.py` 中设置 `OI_PROXY = "volume_5d_growth"` 并记录回退

### ❌ 失误2：忽略否决项的叠加
**后果**：多个否决项同时触发时可能将分数扣到负数，影响买入/卖出信号判断
**修正**：确保最终分数 `max(0, raw_score - total_penalty)`，并在输出中显示否决项明细
**验证**：打印 `score_breakdown` 包含 `veto_deductions`

### ❌ 失误3：混淆 6-Category 和 4-Layer 的权重
**后果**：6 大类的权重（25/20/15/20/10/10）与 4 层权重（55/15/15/15）混用，总分不等于 100
**修正**：在 `scoring_engine.py` 中根据 `framework` 参数选择不同的权重字典，不要同时加载两套权重
**验证**：`assert abs(sum(weights.values()) - 1.0) < 1e-6`

### ❌ 失误4：在 ADX<15 时仍给出买入信号
**后果**：趋势强度太弱，假突破频繁，回测收益差
**修正**：将 ADX<15 作为否决项，扣 20 分；最终分数通常低于买入阈值
**验证**：ADX  extreme 时，即使 L1-L4 原始分高，也应被否决

### ❌ 失误5：前高突破只看收盘价
**后果**：忽略盘中上影线，把冲高回落误判为突破
**修正**：前高突破要求收盘价 > 过去 20 日最高价 × 0.995，且当日振幅不宜过大
**验证**：结合 ATR 百分位排除异常波动

### ❌ 失误6：高费率场景下不做调整
**后果**：期货高频交易手续费侵蚀利润，回测过于乐观
**修正**：将手续费率纳入 `VETO_RULES`，并在 `simulated_broker.py` 中使用真实费率
**验证**：手续费 > 0.05% 时扣 10 分，回测中按实际费率扣除

## 【强调标记】关键约束

> ⚠️ **警告**：以下约束必须严格遵守，否则可能导致策略失效或回测失真

1. **禁止**在 4-Layer 框架中同时使用 6-Category 的权重（必须二选一）
2. **禁止**无 OI 数据时仍硬编码 OI 因子计算（必须有 proxy 回退）
3. **禁止**否决项扣分后最终分数为负数（必须 clamp 到 0）
4. **禁止**忽略 `ADX<15` 的否决项（这是框架的核心风控）
5. **禁止**将 4-Layer 框架用于无成交量或流动性的标的（如小市值 ST 股）
6. **禁止**在回测中不体现手续费、滑点、市场冲击（尤其期货）
7. **推荐**：首次使用 4-Layer 框架时，先在指数期货（如 IF、IC）上验证
8. **推荐**：将 L1-L4 各层分数和否决项明细输出到 `scores_4layer.csv`，便于调试
9. **禁止**：在波动率(波动率)维度盲目上大模型 TSFM（Moirai / TimesFM / TimeGPT 等）。arXiv:2607.05291 证明它们对 HAR 无全面碾压；应使用 Log-HAR + TTM(<1M 参数) **等权集成**，进入 Model Confidence Set 的比例（98–100%）高于任一单模型
10. **强制**：TTM 依赖 `granite-tsfm` 包，必须懒加载且仅在 `VOL_USE_TTM=True` 时启用；包缺失或加载失败时 `EnsembleVolForecaster` 必须自动回退到 Log-HAR（设置 `ttm_available=False`），不得报错中断整个评分流程
11. **禁止**：对存在序列相关的信号（收益率/波动率等）用 **IID 自助法**做不确定性量化。arXiv:2607.06690 证明 IID 自助法在依赖数据下会**严重低覆盖**（区间过窄→过度加仓）；必须使用**依赖感知**的移动块（或 sieve）自助法，`uncertainty_quantification.py` 已默认移动块
12. **强制**：`uncertainty_quantification.py` 主路径依赖 `tsbootstrap` 包，必须优雅回退——包缺失时自动切换纯 numpy 移动块实现（`backend="numpy-fallback"`），不得中断评分
13. **推荐**：将 `confidence`/`risk_scale` 作为仓位乘子（精确信号满仓、噪声信号缩仓）；用 `edge_significant`（CI 排除零）作为"信号非噪声"的风控闸门，与 4-Layer 否决项叠加使用
14. **强制**：任何"方向性准确率/涨跌预测"类 ML 信号（含 TSFM、TimesFM、LoRA 适配模型）必须通过**基率诚实显著性检验**（arXiv:2607.12248）：其命中率 CI 下界须高于市场上涨基率，否则 `risk_scale` 降至 floor；不得将"高方向准确率"直接当作可加仓信号
15. **强制**：相关性/广度类因子（市场广度、板块协同）必须使用**去噪相关矩阵**（arXiv:2607.10297）；禁止在短窗口原始相关矩阵上做板块聚类/危机判定（窗口 < 60 观察值会导致聚类不稳定）
16. **推荐**（⚠️ **已被 #31 修订，须与 #31 合并阅读**）：危机/regime 判定应加入**领先指标**——协方差矩阵特征向量旋转率（arXiv:2607.11935），在波动率爆发前提前收紧否决项与 `risk_scale`；默认用"顶层主成分载荷周度变化"代理，TVP-Kalman 为可选
17. **强制**：尾部风险/CVaR 估计必须采用**时间感知（block/diachronic）采样**（arXiv:2607.10810），与 §13.7 的"禁止 IID 自助法"规则一致；禁止用 i.i.d. 历史样本直接估计 VaR/CVaR
18. **推荐**：新闻情绪作为**低频另类数据叠加**，权重宜小（如 fundamental 桶 5%），仅作确认层/软否决，不与动量因子重复计数；加密标的可叠加 on-chain 情绪（arXiv:2607.15258）
19. **强制**：因子治理（正交化/走航/衰减/熔断/三级评估链）默认全部关闭，必须由 `config.py` 的 `ENABLE_GOVERNANCE` / `GOV_*` 显式开启；禁止为"顺手启用"将默认值改为 `True`
20. **强制**：因子分值相关性 > `GOV_CORR_THRESHOLD`(0.7) 的冗余因子必须剔除并重新归一化权重（`govern_scores`）；禁止在高冗余下直接叠加权重导致因子重复计数
21. **强制**：`CircuitBreaker` 一旦 `tripped()`，`SignalGenerator.generate_signals` **必须**返回空信号帧；禁止在信号路径中静默绕过熔断（try/except 吞掉、强制回退历史信号均属违规）
22. **强制**：评估结果落盘必须走 `atomic_write`（临时文件 + `os.replace`），模块间通信统一使用 `FactorEvaluation` 契约；禁止无契约持久化（裸写结构漂移的 dict）
23. **推荐**：因子准入/淘汰优先走三级评估链（`evaluate_factor_3level`）与走航验证（`walk_forward_validate`）；L2 经济逻辑需 `≥ 3/4` 维通过，L3 必须做 Bonferroni + BH-FDR 多重检验校正
24. **推荐**：走航验证（`GOV_WALK_FORWARD`）与衰减检验（`GOV_DECAY_TEST`）开启时，IC 一致性/衰减率不达标应触发因子剔除或降级，而非仅打印告警
25. **强制**：任何回测在被采信前必须通过 `audit_checklist()`（arXiv:2607.19453/2607.20168）：标签视界 purge + embargo、次日开盘价入场（禁止 same-close 入场）、时点宇宙（禁止全样本筛选后再切分）、预算对齐 + 族错校正后再比模型；任一项不过 → 结果标记 UNRELIABLE，禁止进入因子准入
26. **强制**：不平衡标签（极值/顶底/涨停等）分类器**禁止**只报 ROC-AUC；必须同时给出 average precision 与净费后 P&L（arXiv:2607.19453 实证 AUC 0.87–0.90 仍净亏 44%）
27. **强制**：因子准入采用三闸门合取（arXiv:2607.20093）：统计闸（多重校正后显著）× 经济闸（费后为正）× 生存闸（杠杆下破产概率达标）；三者同时通过才可全权重进入，"未显著"只可判 INCONCLUSIVE 降权，禁止当作"已验证"
28. **推荐**：概率/区间型信号源接入 Brier + Winkler 校准评分（arXiv:2607.16229，严格时间门控），以校准技能分作为 `risk_scale` 的乘子——过度自信的信号源结构性缩仓；不足 60 个已计分预测前不得启用该乘子
29. **推荐**：趋势/动量因子的回看窗口按**成本最优 span**（arXiv:2607.19497）选取而非固定 20/60/120；标的是否适合趋势跟随以低频谱质量（excess spectral mass）诊断为准，样本 < 250 时回退固定窗口
30. **推荐**：组合分散化用 TDA 拓扑距离聚类 + 保留机制滞回换仓（arXiv:2607.21170，得分差 > 10 分才换仓以控制换手），regime/广度判定仍用 §13.8.3 去噪相关——两者用途不得混用；CVaR 优化权重天然集中（arXiv:2607.16450），必须叠加单标的/单行业上限，且回测同时报告 Sharpe 型与 Rachev 型指标并在两者排名冲突时显式标记
31. **强制**（修订 #16）：危机/regime 早期预警（临界慢化族：方差、AC(1)、特征值、§13.8.4 特征向量旋转）**只对内生累积型崩塌有效**，对外生冲击型（政策/关税/突发新闻）结构性失灵（arXiv:2607.27070：7 次事件中 2 次外生冲击完全无信号）。因此：早期预警输出必须是**群体层面先验**（带类型标注的字典，非裸布尔告警），对 `risk_scale` 的影响须设上限（建议 ≤ 30%）；**禁止**把早期预警当作唯一尾部防线——`tail_risk_gate`、单标的上限、非对称波动 CVaR 必须**全时段常备**。任何临界慢化类结论必须报告扫描的分析配置数并通过 placebo/onset 检验，单一调参配置不构成证据
32. **强制**：因子/模型**替换**（非首次准入）必须走前瞻门控 `shadow_before_swap`（arXiv:2607.28577）：挑战者在服务路径外热重训，与在位者在**同一段前瞻延迟标签**上做**配对**比较，净优势超过固定 margin 才晋升；**禁止**按日历定期换模型、**禁止**凭回测 IC 更高就替换在位因子。晋升率过高说明 margin 过松（论文中 528 个挑战者仅晋升 114 个，部署变更减少 78.4%）。点预测因子用配对正当评分（方向用 Brier、分位数用 pinball）代替配对 NLL
33. **强制**：三闸门准入（#27）之前必须先过**有效样本量闸门** `effective_sample_gate`（arXiv:2607.27544）：用自相关修正 `ESS ≈ n/(1+2Σρ_k)` 计算有效独立观测数（重叠窗口与序列相关会严重虚增原始 n）。落入"信号不足区"时判定 `INSUFFICIENT_EVIDENCE`（区别于 INCONCLUSIVE：后者是"测过但未解决"，前者是"根本不可测"），此时**成绩记录不可采信**，只能退回**过程准则**——即 §14.2 的 L2 经济逻辑四维 rubric（需 ≥ 3/4）并施加硬权重上限。同理，低 ESS 的实盘业绩不得用于加杠杆或宣称能力
34. **强制**：区间型输出（`ci_low`/`ci_high`、波动率预测区间、分位数预测）在进入仓位乘子之前必须做**相干性投影** `project_coherent_intervals`（arXiv:2607.26792，KQSP：免训练、免参数、模型无关）：分位数单调、OHLC 序关系、`ci_low ≤ point ≤ ci_high`、RV 区间非负。投影**只保证相干、不保证覆盖**，必须在共形校准**之后**执行，不得替代校准；投影修正幅度须记录，幅度大说明上游预测器失准，应喂给 §13.9.3 校准乘子而非静默修复
35. **强制**：回测**禁止**假设限价单零成本成交（arXiv:2607.28323）。被动成交必须建模：成交概率随报价距中价按指数衰减 `p_fill ≈ exp(−δ/κ)`、被动冲击随距离指数衰减且非零、以概率 `1−p_fill` 的**未成交风险**必须显式入账（错过交易或事后穿价二选一，静默假设成交属前视偏差）。该项加入 `audit_checklist()`，未勾选 ⇒ 结果标记 UNRELIABLE；4-Layer 的高费率否决项须把预期被动冲击与未成交成本计入费率估计
36. **推荐**：A 股拥挤度用羊群效应指标 `herding_indicator`（arXiv:2607.27063：CSAD / LSV / Johnson SU 变换后的滚动尾部指标，三者应同向，背离视为数据质量告警）。定位为**同步压力读数**（在重大扰动期上升），**不得**宣称为领先指标；羊群高位 + 斜率衰减 + 价格相对信号隐含值过度延展 ⇒ 动量衰竭/反转风险，作为新开动量仓的**软否决**（缩 `risk_scale`），**不得**据此做空。羊群走强预示超额峰度上升，应同步抬高 `tail_risk_gate` 的 CVaR 损失预算要求
37. **推荐**：新闻情绪评分器可升级为**市场对齐**范式（arXiv:2607.28127：以已实现前瞻收益 + 非对称奖励做 RL 训练，替代静态人工标注），但——(a) 直接在目标上训练**过拟合面显著扩大**，其回测宣称（如 +220%）必须先过 `audit_checklist()`（§13.9.6）；(b) 重训后的情绪模型只能经 `shadow_before_swap`（#32）晋升；(c) 权重仍受 #18 约束（低频叠加、fundamental 桶约 5%），不得因"RL 版更强"而放大
38. **推荐**：共形 Kelly 仓位（arXiv:2608.01494）——用共形区间**宽度**（§13.7）映射分数 Kelly 乘子（宽→缩、窄→放），`kelly_fraction ≤ 0.5`，区间必须用**慢速、不加权、按标的滚动分位**（宽度稳定优于局部锐利，任何加速自适应会掉 0.7–5.3pt 年化），先过 #34 相干投影 + §13.9.3 校准再入仓；下侧覆盖被突破超历史率时**降杠杆**（非方向信号）。⚠️ 该论文自身为反面教材：200 配置 agentic 搜索开发窗 28.5% CAGR，封存 2022+ 数据并预注册后跌至 8.5%/7.0%（低于被动）——**校准成立 ≠ 增长成立**；任何配置必须封存/预注册并过 `audit_checklist()`(#25) + ESS 闸(#33) 方可采信
39. **推荐**：相关/广度/聚类**结构**优先按**因子暴露相似度**建图（MINGLE，arXiv:2608.06618）而非观测共动——暴露图更贴合经济板块、跨波动率/成本更稳；接入 §13.8.3 广度、§13.9.5 分散聚类、§13.10.1 协方差。缺因子载荷（IPO/短史）**优雅回退**去噪相关图 / CD-DFM 零样本协方差；暴露图与相关图**分歧视为数据质量告警**，#30 单标的/行业上限全时段常备
40. **强制**：回撤预算必须**区分四项度量**（最大回撤 / 最大亏损 / 最长负收益时间 / 最长恢复时间，arXiv:2608.00127），**禁止**用单一高斯回撤表（会误警）；须按策略自身偏度/峰度/波动聚集做蒙特卡洛标定。长记忆（H≠0.5）下最大回撤**深度**按 **T^(H−1/2)** 而非 √T 标度——这是**时间标度校准问题，不得当作内生新风险**（与 #11/#17 无 IID/高斯规则一致，精化 §13.10.2）；四项须分别报告，不得塌缩为单一回撤数
41. **推荐**：组合配置可用**认证型 Wasserstein 分布鲁棒**求解（arXiv:2608.07032）：一范数地度量 + 多面体约束下退化为**多项式规模 LP**，近似误差**同时**界定鲁棒值误差与近优间隙——须把该误差界作为**配置证书**记录。歧义半径由估计不确定性设定（接 ESS #33：有效样本越小半径越大）；半径过大 → 过度保守近等权，须按 `audit_checklist()` 下 OOS 调参，#30 上限常备；LP 不可行或标的数小时回退 CVaR/均值方差
42. **推荐**：模型/预测**换代或跨 run 变化**须做**预测差归因**（合作博弈，arXiv:2608.04547）：把总变化**可加、可对账**地分解到各输入（组合/宏观/模型/假设/人工调整），默认**嵌套 Shapley**（层级输入），不可行时回退 Kernel SHAP 并记录估计器。接入 `shadow_before_swap`(#32)——晋升挑战者前须报告其优势归因，优势若**全由单一波动输入驱动**则为降级标记。归因只解释变化、**不验证优劣**，仍须过三闸门(#27) + ESS 闸(#33)
43. **强制**：新闻情绪因子**禁止**以分类准确率/F1 定权或采信（arXiv:2608.04200：Mistral-7B acc 0.884，但 28 个 model-horizon 前瞻 IC 经 Newey-West + FDR 校正后**无一显著**，最大仅 0.0143）；准入须以**多重校正后仍显著的前瞻收益秩 IC** 为准（接 #27 三闸门、#25 审计）。QLoRA 仅用于**编码器适配**，未过 IC 校正前情绪权重保持 #18 小上限（fundamental 桶约 5%），只作软确认、**绝不作 sizer**；与 #37 市场对齐 RL 过拟合告警一致
44. **推荐**：横截面评分应显式建模**板块异质性**（arXiv:2608.05755：LSTM + 可学习板块嵌入 + 宏观协变量优于池化模型，信号 = 短期反转 + 行业动量）——允许**按板块条件归一化/嵌入**而非全体池化，可新增短期反转子因子（与行业动量并列，均过 #27/#33）。资金流可加**知情流持续性**读数（arXiv:2608.04373：知情度是持续的个体属性）——A 股类比为**龙虎榜席位知情度持续性**（按席位事后前瞻收益排序），仅作**小幅资金流确认**；因 T+1 延迟、席位级粗粒度、可被操纵，须经 ESS 闸(#33)，定位为**同步/短周期确认而非领先**（与 #31 一致）
45. **强制**：L4 实盘反馈必须接入**自动重校准审计**——`auto_recalibrate_watch` 触发的 challenger 只能经 `shadow_before_swap`（#32）晋升，**禁止**自动直接替换在位模型；重训触发须受 `CircuitBreaker`（#21）兜底防止抖动式反复换模（§15.2）。自动重校准产出的是候选 challenger，不是上线动作
46. **强制**：任何**在线学习 / 权重热替换**禁止**静默绕过**——必须先走 `shadow_before_swap`（#32）配对比较，净优势超 margin 才晋升，且同样过 ESS 闸（#33）与三闸门（#27）；低 ESS 下在线更新只能作流程准则降级处理（§15.3）。本条旨在防"热权重漂移"型静默绕过（SkillEvolver 关键失败模式之一），而非禁止学习

47. **推荐**：波动率集成应采用 **regime 路由门控**（arXiv:2608.12251）——regime 状态**仅**用于专家路由，禁止作为预测特征直接拼接；soft routing 优于 hard routing；无 regime 状态则退化为容量匹配 MLP，不报错。
48. **强制**：量化/低精度部署的激活校准窗口须覆盖当前市场离散度 regime（arXiv:2608.12259）——4-bit 下 abs-max 静态校准抹掉可达 62% IC，须用 percentile 校准且监控测试期离散度 vs 校准历史；超出则降级至 8-bit / weight-only 4-bit，禁止在覆盖不足时强行 4-bit 部署。
49. **推荐**：信号触发应**解耦 alpha/beta 腿并取 OR 而非 AND**（arXiv:2608.12283）——pure-alpha 与 pure-beta 独立触发通常优于两者交集；epistemic 不确定性须注入协方差收缩（呼应 §13.7），情绪编码器仅作软确认、受 #18 上限；与 #43 情绪 IC 校正一致。
50. **强制**：经大组件空间搜索得到的策略，其 in-sample 满足率须做 **deflation**（arXiv:2608.10410）——对搜索宽度、时间留痕、随机装配零模型校正；`null_p` 不显著方可采信；结果须接入 `audit_checklist()`（#25），禁止以表观信息比冒充规范满足。
51. **推荐**：系统性风险监控应分离 **inter-sectoral 失衡**（arXiv:2608.12023）——结构失衡主要源于行业间交互；新增 `intersectoral_imbalance_index`，`inter` 分量上升收紧否决项/降 `risk_scale`；无板块标签退化为全局极化，仅作监控。
52. **推荐**：市场同步/分散度除上谱 PCA 外，应补 **下谱（最小特征值）同步因子**（arXiv:2608.09641）——相关矩阵最小特征值含有效结构信息（描述+预测双验证）；标的过少退化为上谱主导因子，下谱仅辅助确认。
53. **推荐**：波动率预测应叠加 **事件日历预公告闸门**（arXiv:2608.10693）——FOMC 等预定会议前 N 日收窄 sizer、抬升 `risk_scale`；无 IV 曲面仅用日历窗口，非美股退化为通用事件闸门（财报/央行）。
54. **强制**：受限市场/指数调整的 **分类边界邻近**须作组合监控状态（arXiv:2608.12634）——ST、指数调入调出、通股通标的变动等临近边界或规则分歧时标记 `MONITOR`，**禁止**当作可交易 alpha 或 sizer；仅触发集中度/再分类监控，与 #43 准入纪律一致。

## §14 因子治理模块（FTS 派生的 6 项工程化能力）

> 来源：微信公众号《FTS：一套贯彻 Harness 工程规范的 AI 原生量化因子系统》。
> 实现：`scripts/factor_governance.py`，全部 **config 驱动、默认关闭**，与 §11–§13 的 arXiv 模块保持同一 opt-in 范式。
> 启用：在 `config.py` 将 `ENABLE_GOVERNANCE` / `GOV_*` 置 `True`，或在构造时传 `enable_governance=True` / `circuit_breaker=...`。

### 14.1 能力清单

| # | 能力 | 入口 | 接入的管线环节 |
|---|------|------|----------------|
| 1 | 契约先行 (TypedDict) + 原子持久化 | `FactorEvaluation` / `atomic_write` | 评估/治理结果落盘 |
| 2 | 三级评估链 L1回测 / L2经济逻辑 / L3多重检验 | `evaluate_factor_3level` | 因子准入（可编排进评分前置） |
| 3 | 走航验证 (Walk-forward) | `walk_forward_validate` | `BacktestEngine.run_walk_forward_validation` |
| 4 | 因子衰减检验 (Decay Test) | `factor_decay_test` | `BacktestEngine.run_decay_test` |
| 5 | 熔断机制 (Circuit Breaker) | `CircuitBreaker` | `SignalGenerator(circuit_breaker=...)` |
| 6 | 正交化 (Orthogonalization) | `orthogonalize_factors` / `govern_scores` | `MultiFactorScorer.calculate_scores` Step 2b |

### 14.2 关键契约与默认值

- **正交化阈值**：`GOV_CORR_THRESHOLD = 0.7`，因子分值相关性 >0.7 成对因子贪心剔除后者（保留先出现者），权重在保留因子上重新归一化。
- **走航验证**：`GOV_WALK_FORWARD` 关闭时 `run_walk_forward_validation` 直接返回 `None`（无副作用）；开启后要求滚动窗口 `mean_ic > 0.03` 且 `consistency ≥ 0.75`。
- **衰减检验**：`GOV_DECAY_WINDOW = 126`（≈6 月交易日），`GOV_DECAY_THRESHOLD = 0.30`，近期 IC 相对历史衰减 `> 30%` → 标记剔除。
- **熔断三类触发**：单日 token 超预算 2×、连续 3 代 `IC < 0.01`、失败率 `> 90%`；熔断后 `generate_signals` 必须返回空信号，不得绕过。
- **三级评估链 L2**：经济逻辑四维（theory/behavior/microstructure/institution）默认 rubric 见 `config.GOV_ECONOMIC_RUBRIC`，需 `≥ 3/4` 通过；L3 用 Bonferroni + BH-FDR 校正。
- **原子持久化**：`atomic_write` 写临时文件后 `os.replace`，中途崩溃不产生半截文件；评估结果统一走 `FactorEvaluation` 契约。

### 14.3 调用示例

```python
from scoring_engine import MultiFactorScorer
from signal_generator import SignalGenerator
from factor_governance import CircuitBreaker

scorer = MultiFactorScorer(enable_governance=True)          # 正交化去冗余
scores = scorer.calculate_scores(data, fundamentals, macro)

cb = CircuitBreaker(token_budget_daily=2_000_000)           # 自动化跑批安全网
gen = SignalGenerator(circuit_breaker=cb)
signals = gen.generate_signals(scores, realized_ic=0.05, passed=True)  # 熔断则空
```

## §15 FTS 差距矩阵映射：能力演进路线（2026-08-11）

> **来源**：FTS 能力差距总览矩阵（L1~L4 × T1/T2/T3 机构对标）。本技能已覆盖多数 T1/T2 维度；以下仅就 T3（海外顶级）差距中**属于技能范畴**的 5 项给出演进路线，明确哪些纳入技能、哪些标注为外部依赖（呼应 skillevolver「精准修订、不过拟合单实例」原则）。

### §15.1 实时成本监控与冲击成本实证标定
**Gap（T3）**：L2 过拟合控制缺实时成本监控；基础层回溯复盘缺冲击成本实证标定 / 融资成本。
**Framework mapping**：升级 §13.10.6 被动市场冲击与未成交风险。
- `cost_calibration_loop(fills, ref_prices)`: 用实盘成交滑点分布定期重估 `p_fill ≈ exp(−δ/κ)` 的 `κ` 与被动冲击系数，写回 `SimulatedBroker`，并触发 `audit_checklist()` 重标（#35）。
- 融资成本（融券/保证金）作为固定日费计入 `tail_risk_gate` 损失预算。
- 默认关闭，配置 `ENABLE_LIVE_COST_CALIB=True` 时启用；缺实盘数据则保留 §13.10.6 理论值并记日志。
- **Caveat**：实证标定须用同标的同周期实盘成交，禁止用模拟盘滑点反标（前视偏差）。

### §15.2 自动重校准触发器（核心优先级）
**Gap（T3）**：L4 反馈闭环缺自动重校准。
**Framework mapping**：在 §13.10.3 `shadow_before_swap` 与 §13.10.4 `effective_sample_gate` 基础上新增触发协议。
- `auto_recalibrate_watch(live_ic, bt_ic, ess)`: 当 `|live_ic − bt_ic|` 持续超过 `RECALIB_IC_GAP`（默认 0.02）且 `ESS ≥ ESS_MIN` 时，自动在 shadow 路径外热重训 challenger；晋升仍须过 #32 配对比较（margin 固定），**禁止**日历式或自动直接替换在位模型。
- 重训触发频率受 `CircuitBreaker`（#21）兜底，避免抖动式反复换模。
- **Caveat**：自动重校准不是自动上线——它只产出候选 challenger，最终晋升由 #32 门控决定。

### §15.3 在线学习护栏（核心优先级）
**Gap（T3）**：L4 在线监控缺在线学习 / 实时重标定深度。
**Framework mapping**：强化 #32 / #37 / #43 的「禁止静默替换」语义。
- **强制**：任何 online update（增量训练、权重热替换、RL 在线策略更新）**不得**直接替换在位模型权重；必须先走 `shadow_before_swap` 配对比较，净优势超 margin 才晋升。
- 在线学习得到的模型同样须过 ESS 闸（#33）与三闸门（#27）方可放量；低 ESS 下在线更新只能作流程准则降级处理。
- 与 §13.10.7 市场对齐 RL 过拟合告警一致：直接在目标上在线训练扩大过拟合面，必须封存/预注册并过 `audit_checklist()`（#25）。
- **Caveat**：本护栏目的是防「热权重漂移」型静默绕过（SkillEvolver 关键失败模式之一），而非禁止学习。

### §15.4 ML 组合层范围边界
**Gap（T3）**：L3 组合层 / 优化器缺 ML 组合层（Transformer/GAN/RL 组合器）。
**Framework mapping**：界定技能当前范围，防止范围蔓延。
- 技能当前组合层 = Elastic Net + Regime 切换 + 风险平价/均值方差 + Ledoit-Wolf 收缩（§14.2）；**维持**此实现为默认。
- ML 组合器（learning-to-rank、RL 配置、Transformer 时序组合）列为**路线图项**，默认禁用；启用前必须：(a) 经 `shadow_before_swap`（#32）晋升；(b) 过 `audit_checklist()`（#25）；(c) 保留单标的/单行业上限（#30）。
- 与 #9（禁止盲目上大模型 TSFM）一致：ML 组合器须有 MCS / 多重检验支撑，不得仅凭回测 Sharpe 上线。

### §15.5 另类数据准入边界
**Gap（T3）**：L1 知识补给 / 基础数据深度缺海外另类数据（卫星、供应链）。
**Framework mapping**：明确技能只做**准入审计**，不内建另类数据抓取。
- 卫星/供应链/舆情图谱等另类数据经外部 pipeline 接入，技能仅负责其因子化后的准入：须过前瞻收益秩 IC（#43 校正）与 ESS 闸（#33），未过则保持小权重软确认（#18）。
- 与 §13.8.6 新闻情绪、§13.10.7 市场对齐 RL 情绪保持同一套「分类≠收益」护栏。
- **Caveat**：另类数据常含非结构化/低频/口径漂移，必须在 `cost_calibration_loop` 之外单独做时点对齐（point-in-time）校验，禁止未来函数。

**本周主题**：把「实盘反馈 → 重校准 → 在线学习」闭环作为技能的**第三类治理对象**（与 §14 因子治理并列），并以 scope boundary 防止 ML 组合器 / 另类数据的范围蔓延。

## 版本历史

| 版本 | 日期 | 变更说明 |
|------|------|---------|
| v2.0.0 | 2026-07-01 | SkillEvolver + Loop 演化：新增 4-Layer 评分框架（萌芽/量价/结构/确认）、否决项规则、期货/衍生品 OI 数据说明、4-Layer config 示例、S_appendix 双层结构 |
| v2.1.0 | 2026-07-11 | SkillEvolver 演化（arXiv:2607.05291）：新增波动率预测模块 `volatility_forecaster.py`，实现 Log-HAR + TTM 等权集成（带 TTM 缺失优雅回退与 Mincer-Zarnowitz 重校准），接入 `MultiFactorScorer` 为可选 `volatility` 维度分数（config 驱动，默认关闭） |
| v2.2.0 | 2026-07-11 | SkillEvolver 演化（arXiv:2607.06690）：新增无分布不确定性量化模块 `uncertainty_quantification.py`，实现依赖感知移动块自助法 CI（tsbootstrap 主路径 + 纯numpy回退）、split-conformal 预测半宽、仓位置信度映射与风控闸门（CI跨零则否决），接入 `MultiFactorScorer` 为可选 `confidence`/`ci_low`/`ci_high`/`edge_significant`/`risk_scale` 字段（config 驱动，默认关闭） |
| v2.3.0 | 2026-07-18 | SkillEvolver 周度自进化（arXiv 2026-07-14~18）：新增 6 篇本周论文集成 — §13.8.1 成本感知多期配置(arXiv:2607.15195)、§13.8.2 基率诚实方向显著性(arXiv:2607.12248)、§13.8.3 去噪相关广度因子(arXiv:2607.10297)、§13.8.4 特征向量旋转危机领先指标(arXiv:2607.11935)、§13.8.5 厚尾风险闸门(arXiv:2607.10810)、§13.8.6 新闻情绪另类因子(arXiv:2607.13968)；新增约束 #14–#18 |
| v2.5.0 | 2026-07-25 | SkillEvolver 周度自进化（arXiv 2026-07-20~24，64 篇扫描选 6）：新增 §13.9 — §13.9.1 趋势跟随谱质量诊断与成本最优 span(arXiv:2607.19497)、§13.9.2 三闸门因子准入(arXiv:2607.20093)、§13.9.3 Brier+Winkler 校准评分乘子(arXiv:2607.16229)、§13.9.4 非对称波动 CVaR 配置与度量分歧标记(arXiv:2607.16450)、§13.9.5 TDA 拓扑分散化+保留滞回换仓(arXiv:2607.21170)、§13.9.6 回测取证清单 audit_checklist(arXiv:2607.19453+2607.20168)；新增约束 #25–#30；修正 frontmatter 版本号漂移（v2.4.0 时未同步） |
| v2.6.0 | 2026-08-02 | SkillEvolver 周度自进化（arXiv 2026-07-27~31，76 篇扫描选 8 篇成 7 节）：新增 §13.10 — §13.10.1 特征驱动协方差 CD-DFM 与零样本标的接入(arXiv:2607.24410)、§13.10.2 早期预警事件异质性护栏（**部分回撤 §13.8.4** 的领先指标定位，arXiv:2607.27070）、§13.10.3 Shadow-Before-Swap 前瞻门控换模/换因子(arXiv:2607.28577)、§13.10.4 有效样本量闸门 ESS 与 INSUFFICIENT_EVIDENCE 判定(arXiv:2607.27544)、§13.10.5 区间相干性投影 KQSP(arXiv:2607.26792)、§13.10.6 被动市场冲击与未成交风险(arXiv:2607.28323)、§13.10.7 A股羊群拥挤度 + 市场对齐情绪 RL(arXiv:2607.27063+2607.28127)；新增约束 #31–#37（其中 #31 为对 #16 的修订） |
| v2.7.0 | 2026-08-10 | SkillEvolver 周度自进化（arXiv 2026-08-04~10，92 篇扫描选 8 篇成 7 节）：新增 §13.11 — §13.11.1 共形 Kelly 区间宽度仓位 + 诚实 OOS 崩塌(arXiv:2608.01494)、§13.11.2 MINGLE 因子暴露相似度建图(arXiv:2608.06618)、§13.11.3 非高斯长记忆回撤预算 T^(H−1/2) 标度(arXiv:2608.00127)、§13.11.4 认证型 Wasserstein 分布鲁棒配置(arXiv:2608.07032)、§13.11.5 预测差 Shapley 归因(arXiv:2608.04547)、§13.11.6 情绪分类≠收益可预测护栏(arXiv:2608.04200)、§13.11.7 板块嵌入横截面异质性 + 知情流/龙虎榜席位持续性(arXiv:2608.05755+2608.04373)；新增约束 #38–#44。本周主题：不确定性→仓位、共动→结构、锐利→稳健（证据纪律贯穿：共形 Kelly OOS 崩塌 / 情绪 IC 无一显著 / 预测差归因） |
| v2.8.0 | 2026-08-11 | SkillEvolver 演化（FTS 差距矩阵 L1-L4×T1/T2/T3 对标）：新增 §15 FTS 差距矩阵映射：能力演进路线 — §15.1 实时成本监控与冲击成本实证标定、§15.2 自动重校准触发器、§15.3 在线学习护栏、§15.4 ML 组合层范围边界、§15.5 另类数据准入边界；新增约束 #45–#46。本周主题：实盘反馈→重校准→在线学习闭环作为第三类治理对象（与 §14 因子治理并列），并以 scope boundary 防 ML 组合器/另类数据范围蔓延 |
| v2.9.0 | 2026-08-16 | SkillEvolver 周度自进化（arXiv 2026-08-10~16，约 120 篇扫描选 8 篇成 8 节 + 1 护栏）：新增 §13.12 — §13.12.1 regime 路由波动率集成(arXiv:2608.12251)、§13.12.2 校准期覆盖部署闸门(arXiv:2608.12259)、§13.12.3 解耦 alpha/beta 触发+认知协方差收缩(arXiv:2608.12283)、§13.12.4 规范满足回测验证(arXiv:2608.10410)、§13.12.5 部门间失衡监控(arXiv:2608.12023)、§13.12.6 下谱同步因子(arXiv:2608.09641)、§13.12.7 FOMC 预公告波动闸门(arXiv:2608.10693)、§13.12.8 分类边界邻近监控(arXiv:2608.12634)；+ 护栏 §13.12 TSI 同步态(arXiv:2608.10788)；新增约束 #47–#54。本周主题：波动率集成回归(regime路由+部署期校准)、信号解耦、回测可取性证明、结构网络、准入边界 |
| v2.4.0 | 2026-07-24 | SkillEvolver + Loop 演化（FTS 文章派生）：新增因子治理模块 `scripts/factor_governance.py`，实现 6 项工程化能力——契约先行(TypedDict)+原子持久化、三级评估链(L1回测/L2经济逻辑/L3多重检验)、走航验证(Walk-forward)、因子衰减检验(Decay Test)、熔断机制(Circuit Breaker)、正交化(去冗余)；接入 `scoring_engine`(正交化)、`signal_generator`(熔断网关)、`backtest`(走航/衰减报告)，全部 config 驱动默认关闭；SKILL.md 新增 §14 与约束 #19–#24 |
| v1.x | 2026-06 | 初始版本：6-Category 多因子评分框架，支持 A股/港股/美股，含 2026 arXiv 研究集成 |

---

**To use this skill:** Ask WorkBuddy to "build a multi-factor scoring trading system", "create a factor-based stock selection model", or "implement a quantitative trading strategy with momentum, technical, and fundamental factors".
