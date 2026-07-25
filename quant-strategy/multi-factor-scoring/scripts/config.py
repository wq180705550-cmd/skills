"""
Configuration file for Multi-Factor Scoring Quantitative Trading System
"""

# Factor weights (must sum to 1.0)
# Users can customize these weights according to their preferences
FACTOR_WEIGHTS = {
    'momentum': 0.25,      # 动量因子
    'technical': 0.20,       # 技术指标
    'volume': 0.15,          # 成交量
    'fundamental': 0.20,     # 基本面
    'macro': 0.10,           # 宏观经济
    'sector': 0.10           # 行业板块
}

# Trading universe - Customize these symbols as needed
SYMBOLS = {
    'ashare': [
        '600519.SH',  # 贵州茅台
        '000858.SZ',  # 五粮液
        '601318.SH',  # 中国平安
        '000333.SZ',  # 美的集团
        '600036.SH',  # 招商银行
    ],
    'hk': [
        '0700.HK',   # 腾讯控股
        '0941.HK',   # 中国移动
        '9988.HK',   # 阿里巴巴
        '3690.HK',   # 美团
        '1810.HK',   # 小米集团
    ],
    'us': [
        'AAPL',      # Apple
        'MSFT',      # Microsoft
        'GOOGL',     # Google
        'AMZN',      # Amazon
        'NVDA',      # NVIDIA
    ]
}

# Timeframes to use
TIMEFRAMES = ['daily', '4h', '1h', '15m']

# Signal generation thresholds
BUY_THRESHOLD_PERCENTILE = 80   # Buy when score is above 80th percentile
SELL_THRESHOLD_PERCENTILE = 20   # Sell when score is below 20th percentile
SCORE_IMPROVEMENT_THRESHOLD = 20  # Buy if score improves by 20+ points
SCORE_DECLINE_THRESHOLD = 20      # Sell if score declines by 20+ points
MIN_SCORE_FOR_BUY = 70            # Minimum score to buy
MAX_SCORE_FOR_SELL = 30           # Maximum score to hold (sell if below)

# Risk management
MAX_POSITION_SIZE = 0.10          # Maximum 10% per stock
MAX_SECTOR_EXPOSURE = 0.30       # Maximum 30% per sector
STOP_LOSS = 0.08                  # 8% stop loss
TAKE_PROFIT = 0.20                # 20% take profit

# Backtest parameters
INITIAL_CAPITAL = 100000           # Initial capital (CNY for A-shares, HKD for HK, USD for US)
COMMISSION = 0.0003                # 0.03% commission
SLIPPAGE = 0.001                  # 0.1% slippage

# Data parameters
DATA_START_DATE = '2023-01-01'
DATA_END_DATE = '2024-12-31'
DATA_CACHE_DIR = 'data/'          # Local cache directory

# Scoring parameters
SCORE_RANGE = (0, 100)           # Score range (min, max)
MOMENTUM_PERIODS = [20, 60, 120]  # Days for momentum calculation (1M, 3M, 6M)
RSI_PERIOD = 14
MACD_PARAMS = (12, 26, 9)
BOLLINGER_PERIOD = 20
BOLLINGER_STD = 2

# Volatility forecasting (arXiv:2607.05291) — Log-HAR + TTM equal-weight ensemble
ENABLE_VOL_FORECAST = False          # Opt-in: adds a 'volatility' dimension score
VOL_HORIZON = 5                      # Forecast horizon (days): 1 (daily), 5 (weekly), 22 (monthly)
VOL_USE_TTM = True                   # Use Tiny Time Mixers in the ensemble (needs `pip install granite-tsfm`)
VOL_CONTEXT_LENGTH = 64              # TTM context length (>=64 recommended for daily RV)
VOL_RECALIBRATE = False              # Mincer-Zarnowitz scale recalibration (uses in-sample LogHAR errors)

# Uncertainty quantification (arXiv:2607.06690) — distribution-free CIs for signals
# Attaches a confidence interval to each symbol's return signal so you can size
# positions by confidence and set risk-control thresholds. IID bootstrap
# undercovers under dependence -> we default to a dependence-aware MOVING BLOCK
# bootstrap (tsbootstrap if installed, else a pure-numpy fallback).
ENABLE_UNCERTAINTY = False           # Opt-in: adds 'confidence' / 'ci_low' / 'ci_high' / 'edge_significant'
UQ_ALPHA = 0.10                      # Miscoverage level -> (1 - alpha) = 90% intervals
UQ_N_BOOTSTRAPS = 500                # Bootstrap replicates (500 is a good speed/accuracy balance)
UQ_CONF_FLOOR = 0.30                 # Minimum position-confidence multiplier (never size to 0 on width alone)
UQ_REQUIRE_SIGNIFICANT = False       # If True, veto (scale->0) when the return CI straddles zero
UQ_RANDOM_STATE = 0                  # Seed for reproducible intervals

# Fundamental data (example values - in practice, fetch from API)
# This is a simplified example; real implementation would fetch from financial data APIs
FUNDAMENTAL_DATA = {
    '600519.SH': {'pe': 35.2, 'pb': 10.5, 'roe': 0.28, 'revenue_growth': 0.15},
    '000858.SZ': {'pe': 25.8, 'pb': 6.2, 'roe': 0.24, 'revenue_growth': 0.12},
    # ... more stocks
}

# Macro economic indicators (example values - in practice, fetch from API)
MACRO_DATA = {
    'interest_rate': 0.0325,    # 10-year government bond yield
    'cpi': 0.020,               # CPI inflation
    'pmi': 50.5,                # Manufacturing PMI
    'gdp_growth': 0.052,        # GDP growth rate
}

# Sector classification (example)
SECTOR_MAP = {
    '600519.SH': 'consumer_staples',
    '000858.SZ': 'consumer_staples',
    '601318.SH': 'financials',
    '000333.SZ': 'consumer_discretionary',
    '600036.SH': 'financials',
    '0700.HK': 'technology',
    '0941.HK': 'telecommunications',
    '9988.HK': 'technology',
    'AAPL': 'technology',
    'MSFT': 'technology',
    'GOOGL': 'technology',
    'AMZN': 'consumer_discretionary',
    'NVDA': 'technology',
}

# =====================================================================
# 因子治理模块 (factor_governance.py) — FTS 派生的 6 项工程化能力
# 默认全部关闭，与现有 arXiv 模块一致（config 驱动，不改动既有行为）
# =====================================================================
ENABLE_GOVERNANCE = False        # 总开关：在 scoring_engine 中启用正交化去冗余
GOV_CORR_THRESHOLD = 0.7         # 正交化相关性阈值：>0.7 剔除冗余因子
GOV_EVAL_CHAIN = False           # 三级评估链（L1回测/L2经济逻辑/L3多重检验）
GOV_WALK_FORWARD = False         # 走航验证（替代单次 train/test）
GOV_DECAY_TEST = False           # 因子衰减检验
GOV_DECAY_WINDOW = 126           # 衰减窗口（≈6 个月交易日）
GOV_DECAY_THRESHOLD = 0.30       # 衰减率阈值：>30% 剔除
GOV_ATOMIC_WRITE = True          # 评估/治理结果原子持久化（temp + os.replace）

# 熔断机制（自动化跑批安全网）默认值
GOV_CB_TOKEN_BUDGET = 2_000_000  # 单日 token 预算
GOV_CB_MAX_TOKEN_MULT = 2.0      # 超预算 2x 熔断
GOV_CB_MIN_IC = 0.01             # 连续低 IC 阈值
GOV_CB_MAX_CONSEC_LOW_IC = 3     # 连续 3 代 IC<0.01 熔断
GOV_CB_MAX_FAILURE_RATE = 0.90   # 失败率 >90% 熔断

# 三级评估链：L2 经济逻辑四维默认 rubric（theory/behavior/microstructure/institution, 0/1）
# 各因子可按需覆盖；此处为 6 大类的默认合理假设
GOV_ECONOMIC_RUBRIC = {
    'momentum':      {'theory': 1, 'behavior': 1, 'microstructure': 1, 'institution': 1},
    'technical':     {'theory': 1, 'behavior': 1, 'microstructure': 1, 'institution': 0},
    'volume':        {'theory': 1, 'behavior': 1, 'microstructure': 1, 'institution': 0},
    'fundamental':   {'theory': 1, 'behavior': 0, 'microstructure': 1, 'institution': 1},
    'macro':         {'theory': 1, 'behavior': 0, 'microstructure': 0, 'institution': 1},
    'sector':        {'theory': 1, 'behavior': 1, 'microstructure': 1, 'institution': 1},
}

