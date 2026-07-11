---
name: multi-factor-scoring
description: "Multi-factor scoring quantitative trading system. Use this skill when the user wants to build a quantitative trading strategy based on multi-factor scoring (momentum, technical indicators, volume, fundamentals, macro, sector rotation), with support for A-shares, HK stocks, US stocks, and futures/derivatives across multiple timeframes (daily, 4H, 1H, 15M). Now includes an optional 4-layer scoring framework (sprout/volume-price/structure/confirmation) with veto rules, and a realized-volatility forecasting module (Log-HAR + TTM equal-weight ensemble, arXiv:2607.05291) for the volatility dimension. Triggers include requests for multi-factor models, scoring systems, factor-based stock selection, rotational strategies, quantitative trading framework setup, 4-layer scoring framework, or volatility forecasting / HAR / Log-HAR / TTM."
agent_created: true
version: 2.1.0
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
keywords: [multi-factor, quantitative-trading, scoring-system, factor-selection, A-shares, HK-stocks, US-stocks, futures, derivatives, OI, ATR, OBV, CMF, Supertrend, HMA, Donchian, DMI, MACD, realized-volatility, HAR, Log-HAR, TTM, TSFM, ensemble, VOLARE]
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

This skill now incorporates cutting-edge research from 11 top arXiv papers (May–July 2026). These features are enabled by default and can be toggled in `scoring_engine.py`, `volatility_forecaster.py`, and `simulated_broker.py`.

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

## 版本历史

| 版本 | 日期 | 变更说明 |
|------|------|---------|
| v2.0.0 | 2026-07-01 | SkillEvolver + Loop 演化：新增 4-Layer 评分框架（萌芽/量价/结构/确认）、否决项规则、期货/衍生品 OI 数据说明、4-Layer config 示例、S_appendix 双层结构 |
| v2.1.0 | 2026-07-11 | SkillEvolver 演化（arXiv:2607.05291）：新增波动率预测模块 `volatility_forecaster.py`，实现 Log-HAR + TTM 等权集成（带 TTM 缺失优雅回退与 Mincer-Zarnowitz 重校准），接入 `MultiFactorScorer` 为可选 `volatility` 维度分数（config 驱动，默认关闭） |
| v1.x | 2026-06 | 初始版本：6-Category 多因子评分框架，支持 A股/港股/美股，含 2026 arXiv 研究集成 |

---

**To use this skill:** Ask WorkBuddy to "build a multi-factor scoring trading system", "create a factor-based stock selection model", or "implement a quantitative trading strategy with momentum, technical, and fundamental factors".
