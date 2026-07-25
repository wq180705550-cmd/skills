---
name: multi-factor-scoring
description: "Multi-factor scoring quantitative trading system. Use this skill when the user wants to build a quantitative trading strategy based on multi-factor scoring (momentum, technical indicators, volume, fundamentals, macro, sector rotation), with support for A-shares, HK stocks, US stocks, and futures/derivatives across multiple timeframes (daily, 4H, 1H, 15M). Now includes an optional 4-layer scoring framework (sprout/volume-price/structure/confirmation) with veto rules, a realized-volatility forecasting module (Log-HAR + TTM equal-weight ensemble, arXiv:2607.05291) for the volatility dimension, and a distribution-free uncertainty-quantification module (dependence-aware bootstrap + conformal confidence intervals, arXiv:2607.06690) that attaches calibrated confidence intervals to signals for position-confidence sizing and risk-control thresholds. Triggers include requests for multi-factor models, scoring systems, factor-based stock selection, rotational strategies, quantitative trading framework setup, 4-layer scoring framework, volatility forecasting / HAR / Log-HAR / TTM, or uncertainty quantification / conformal prediction / bootstrap confidence intervals / position confidence / risk thresholds. Weekly arXiv auto-evolution (2026-07-14~18) adds cost-aware RL allocation (arXiv:2607.15195), base-rate-honest directional-significance testing (arXiv:2607.12248), denoised correlation-breadth factor (arXiv:2607.10297), eigenvector-rotation crisis early-warning (arXiv:2607.11935), fat-tail-aware risk gating (arXiv:2607.10810), and a news-sentiment alternative factor (arXiv:2607.13968). Weekly arXiv auto-evolution (2026-07-20~24) adds trend-following spectral-mass diagnostics with cost-optimal lookback span (arXiv:2607.19497), triple-gate factor admission (statistical x economic x survival, arXiv:2607.20093), Brier+Winkler calibration-based sizing multiplier (arXiv:2607.16229), asymmetric-volatility CVaR allocation with measure-disagreement flagging (arXiv:2607.16450), TDA topological diversification with retention-based turnover control (arXiv:2607.21170), and a backtest forensic audit checklist (purged splits, next-bar entry, AUC-vs-precision guard, point-in-time universe; arXiv:2607.19453 + 2607.20168)."
agent_created: true
version: 2.5.0
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
keywords: [multi-factor, quantitative-trading, scoring-system, factor-selection, A-shares, HK-stocks, US-stocks, futures, derivatives, OI, ATR, OBV, CMF, Supertrend, HMA, Donchian, DMI, MACD, realized-volatility, HAR, Log-HAR, TTM, TSFM, ensemble, VOLARE, uncertainty-quantification, conformal-prediction, block-bootstrap, tsbootstrap, confidence-interval, position-confidence, risk-gate, EnbPI, cost-aware-allocation, SciPhyRL, base-rate, directional-significance, correlation-denoising, market-breadth, eigenvector-rotation, early-warning, tail-risk, CVaR, news-sentiment, alternative-data, trend-following, spectral-mass, cost-optimal-span, triple-gate-admission, backtest-audit, purged-split, calibration, Brier-score, Winkler-score, TDA, topological-clustering, retention-mechanism, GJR-GARCH, asymmetric-volatility, Rachev-ratio]
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
11. **禁止**：对存在序列相关的信号（收益率/波动率等）用 **IID 自助法**做不确定性量化。arXiv:2607.06690 证明 IID 自助法在依赖数据下会**严重低覆盖**（区间过窄→过度加仓）；必须使用**依赖感知**的移动块（或 sieve）自助法，`uncertainty_quantification.py` 已默认移动块
12. **强制**：`uncertainty_quantification.py` 主路径依赖 `tsbootstrap` 包，必须优雅回退——包缺失时自动切换纯 numpy 移动块实现（`backend="numpy-fallback"`），不得中断评分
13. **推荐**：将 `confidence`/`risk_scale` 作为仓位乘子（精确信号满仓、噪声信号缩仓）；用 `edge_significant`（CI 排除零）作为"信号非噪声"的风控闸门，与 4-Layer 否决项叠加使用
14. **强制**：任何"方向性准确率/涨跌预测"类 ML 信号（含 TSFM、TimesFM、LoRA 适配模型）必须通过**基率诚实显著性检验**（arXiv:2607.12248）：其命中率 CI 下界须高于市场上涨基率，否则 `risk_scale` 降至 floor；不得将"高方向准确率"直接当作可加仓信号
15. **强制**：相关性/广度类因子（市场广度、板块协同）必须使用**去噪相关矩阵**（arXiv:2607.10297）；禁止在短窗口原始相关矩阵上做板块聚类/危机判定（窗口 < 60 观察值会导致聚类不稳定）
16. **推荐**：危机/regime 判定应加入**领先指标**——协方差矩阵特征向量旋转率（arXiv:2607.11935），在波动率爆发前提前收紧否决项与 `risk_scale`；默认用"顶层主成分载荷周度变化"代理，TVP-Kalman 为可选
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

## 版本历史

| 版本 | 日期 | 变更说明 |
|------|------|---------|
| v2.0.0 | 2026-07-01 | SkillEvolver + Loop 演化：新增 4-Layer 评分框架（萌芽/量价/结构/确认）、否决项规则、期货/衍生品 OI 数据说明、4-Layer config 示例、S_appendix 双层结构 |
| v2.1.0 | 2026-07-11 | SkillEvolver 演化（arXiv:2607.05291）：新增波动率预测模块 `volatility_forecaster.py`，实现 Log-HAR + TTM 等权集成（带 TTM 缺失优雅回退与 Mincer-Zarnowitz 重校准），接入 `MultiFactorScorer` 为可选 `volatility` 维度分数（config 驱动，默认关闭） |
| v2.2.0 | 2026-07-11 | SkillEvolver 演化（arXiv:2607.06690）：新增无分布不确定性量化模块 `uncertainty_quantification.py`，实现依赖感知移动块自助法 CI（tsbootstrap 主路径 + 纯numpy回退）、split-conformal 预测半宽、仓位置信度映射与风控闸门（CI跨零则否决），接入 `MultiFactorScorer` 为可选 `confidence`/`ci_low`/`ci_high`/`edge_significant`/`risk_scale` 字段（config 驱动，默认关闭） |
| v2.3.0 | 2026-07-18 | SkillEvolver 周度自进化（arXiv 2026-07-14~18）：新增 6 篇本周论文集成 — §13.8.1 成本感知多期配置(arXiv:2607.15195)、§13.8.2 基率诚实方向显著性(arXiv:2607.12248)、§13.8.3 去噪相关广度因子(arXiv:2607.10297)、§13.8.4 特征向量旋转危机领先指标(arXiv:2607.11935)、§13.8.5 厚尾风险闸门(arXiv:2607.10810)、§13.8.6 新闻情绪另类因子(arXiv:2607.13968)；新增约束 #14–#18 |
| v2.5.0 | 2026-07-25 | SkillEvolver 周度自进化（arXiv 2026-07-20~24，64 篇扫描选 6）：新增 §13.9 — §13.9.1 趋势跟随谱质量诊断与成本最优 span(arXiv:2607.19497)、§13.9.2 三闸门因子准入(arXiv:2607.20093)、§13.9.3 Brier+Winkler 校准评分乘子(arXiv:2607.16229)、§13.9.4 非对称波动 CVaR 配置与度量分歧标记(arXiv:2607.16450)、§13.9.5 TDA 拓扑分散化+保留滞回换仓(arXiv:2607.21170)、§13.9.6 回测取证清单 audit_checklist(arXiv:2607.19453+2607.20168)；新增约束 #25–#30；修正 frontmatter 版本号漂移（v2.4.0 时未同步） |
| v2.4.0 | 2026-07-24 | SkillEvolver + Loop 演化（FTS 文章派生）：新增因子治理模块 `scripts/factor_governance.py`，实现 6 项工程化能力——契约先行(TypedDict)+原子持久化、三级评估链(L1回测/L2经济逻辑/L3多重检验)、走航验证(Walk-forward)、因子衰减检验(Decay Test)、熔断机制(Circuit Breaker)、正交化(去冗余)；接入 `scoring_engine`(正交化)、`signal_generator`(熔断网关)、`backtest`(走航/衰减报告)，全部 config 驱动默认关闭；SKILL.md 新增 §14 与约束 #19–#24 |
| v1.x | 2026-06 | 初始版本：6-Category 多因子评分框架，支持 A股/港股/美股，含 2026 arXiv 研究集成 |

---

**To use this skill:** Ask WorkBuddy to "build a multi-factor scoring trading system", "create a factor-based stock selection model", or "implement a quantitative trading strategy with momentum, technical, and fundamental factors".
