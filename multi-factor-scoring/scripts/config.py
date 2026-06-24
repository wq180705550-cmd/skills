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
