"""
Multi-Market Data Loader
Supports A-shares, HK stocks, and US stocks across multiple timeframes
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import json

try:
    import akshare as ak
    AKSHARE_AVAILABLE = True
except ImportError:
    AKSHARE_AVAILABLE = False
    print("Warning: akshare not installed. A-share data will use sample data.")

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    print("Warning: yfinance not installed. US/HK stock data will use sample data.")

from config import *


class MultiMarketDataLoader:
    """Load market data for A-shares, HK stocks, and US stocks"""

    def __init__(self, cache_dir=DATA_CACHE_DIR):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)

    def load_data(self, symbols, start_date, end_date, timeframe='daily'):
        """
        Load data for multiple symbols

        Args:
            symbols: List of stock symbols or dict with market keys
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            timeframe: 'daily', '4h', '1h', '15m'

        Returns:
            dict: {symbol: DataFrame}
        """
        data = {}

        # Handle both list and dict inputs
        if isinstance(symbols, dict):
            all_symbols = []
            for market, syms in symbols.items():
                all_symbols.extend(syms)
        else:
            all_symbols = symbols

        for symbol in all_symbols:
            df = self.load_symbol_data(symbol, start_date, end_date, timeframe)
            if df is not None and not df.empty:
                data[symbol] = df

        return data

    def load_symbol_data(self, symbol, start_date, end_date, timeframe='daily'):
        """Load data for a single symbol"""
        # Check cache first
        cache_file = self._get_cache_filename(symbol, timeframe)
        if os.path.exists(cache_file):
            cache_mtime = os.path.getmtime(cache_file)
            cache_age = (datetime.now().timestamp() - cache_mtime) / 3600
            if cache_age < 24:  # Use cache if less than 24 hours old
                print(f"Loading {symbol} from cache...")
                return pd.read_csv(cache_file, index_col=0, parse_dates=True)

        # Determine market and load data
        if '.SH' in symbol or '.SZ' in symbol:
            df = self._load_ashare_data(symbol, start_date, end_date, timeframe)
        elif '.HK' in symbol:
            df = self._load_hk_data(symbol, start_date, end_date, timeframe)
        else:
            df = self._load_us_data(symbol, start_date, end_date, timeframe)

        # Save to cache
        if df is not None and not df.empty:
            df.to_csv(cache_file)
            print(f"Saved {symbol} data to cache: {cache_file}")

        return df

    def _load_ashare_data(self, symbol, start_date, end_date, timeframe):
        """Load A-share data using akshare"""
        if not AKSHARE_AVAILABLE:
            return self._generate_sample_data(symbol, start_date, end_date)

        try:
            # Convert symbol format: 600519.SH -> sh600519
            if '.SH' in symbol:
                code = 'sh' + symbol.split('.')[0]
            else:
                code = 'sz' + symbol.split('.')[0]

            print(f"Loading A-share data for {symbol} ({code})...")

            # Load daily data
            df = ak.stock_zh_a_hist(
                symbol=code,
                period="daily",
                start_date=start_date.replace('-', ''),
                end_date=end_date.replace('-', ''),
                adjust="qfq"  # Forward adjust for dividends and splits
            )

            if df is None or df.empty:
                print(f"No data found for {symbol}")
                return self._generate_sample_data(symbol, start_date, end_date)

            # Standardize column names
            df = df.rename(columns={
                '日期': 'date',
                '开盘': 'open',
                '收盘': 'close',
                '最高': 'high',
                '最低': 'low',
                '成交量': 'volume',
                '成交额': 'amount'
            })

            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            df = df[['open', 'high', 'low', 'close', 'volume']]

            # Resample if timeframe != daily
            if timeframe != 'daily':
                df = self._resample_data(df, timeframe)

            return df

        except Exception as e:
            print(f"Error loading A-share data for {symbol}: {e}")
            return self._generate_sample_data(symbol, start_date, end_date)

    def _load_hk_data(self, symbol, start_date, end_date, timeframe):
        """Load HK stock data using yfinance"""
        if not YFINANCE_AVAILABLE:
            return self._generate_sample_data(symbol, start_date, end_date)

        try:
            print(f"Loading HK stock data for {symbol}...")

            ticker = yf.Ticker(symbol)
            df = ticker.history(start=start_date, end=end_date)

            if df is None or df.empty:
                print(f"No data found for {symbol}")
                return self._generate_sample_data(symbol, start_date, end_date)

            df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
            df.columns = ['open', 'high', 'low', 'close', 'volume']

            # Resample if timeframe != daily
            if timeframe != 'daily':
                df = self._resample_data(df, timeframe)

            return df

        except Exception as e:
            print(f"Error loading HK stock data for {symbol}: {e}")
            return self._generate_sample_data(symbol, start_date, end_date)

    def _load_us_data(self, symbol, start_date, end_date, timeframe):
        """Load US stock data using yfinance"""
        if not YFINANCE_AVAILABLE:
            return self._generate_sample_data(symbol, start_date, end_date)

        try:
            print(f"Loading US stock data for {symbol}...")

            ticker = yf.Ticker(symbol)
            df = ticker.history(start=start_date, end=end_date)

            if df is None or df.empty:
                print(f"No data found for {symbol}")
                return self._generate_sample_data(symbol, start_date, end_date)

            df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
            df.columns = ['open', 'high', 'low', 'close', 'volume']

            # Resample if timeframe != daily
            if timeframe != 'daily':
                df = self._resample_data(df, timeframe)

            return df

        except Exception as e:
            print(f"Error loading US stock data for {symbol}: {e}")
            return self._generate_sample_data(symbol, start_date, end_date)

    def _resample_data(self, df, timeframe):
        """Resample data to different timeframes"""
        timeframe_map = {
            '4h': '4H',
            '1h': '1H',
            '15m': '15min'
        }

        if timeframe not in timeframe_map:
            return df

        rule = timeframe_map[timeframe]

        df_resampled = df.resample(rule).agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }).dropna()

        return df_resampled

    def _get_cache_filename(self, symbol, timeframe):
        """Generate cache filename for a symbol"""
        safe_symbol = symbol.replace('.', '_')
        return os.path.join(self.cache_dir, f"{safe_symbol}_{timeframe}.csv")

    def _generate_sample_data(self, symbol, start_date, end_date):
        """Generate sample data for testing"""
        print(f"Generating sample data for {symbol}...")
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        n = len(dates)

        np.random.seed(hash(symbol) % 2**32)
        returns = np.random.normal(0.0005, 0.02, n)
        prices = 100 * np.exp(np.cumsum(returns))

        df = pd.DataFrame({
            'open': prices * (1 + np.random.uniform(-0.01, 0.01, n)),
            'high': prices * (1 + np.random.uniform(0, 0.02, n)),
            'low': prices * (1 + np.random.uniform(-0.02, 0, n)),
            'close': prices,
            'volume': np.random.randint(1000000, 10000000, n)
        }, index=dates)

        return df

    def load_fundamental_data(self, symbols):
        """Load fundamental data for symbols"""
        # In practice, this would fetch from financial data APIs
        # For now, return sample data from config
        fundamentals = {}

        for symbol in symbols:
            if symbol in FUNDAMENTAL_DATA:
                fundamentals[symbol] = FUNDAMENTAL_DATA[symbol]
            else:
                # Generate random fundamental data
                fundamentals[symbol] = {
                    'pe': np.random.uniform(10, 50),
                    'pb': np.random.uniform(1, 10),
                    'roe': np.random.uniform(0.05, 0.30),
                    'revenue_growth': np.random.uniform(-0.1, 0.3)
                }

        return fundamentals

    def load_macro_data(self):
        """Load macroeconomic indicators"""
        # In practice, this would fetch from macro APIs
        # For now, return sample data from config
        return MACRO_DATA


if __name__ == "__main__":
    # Test the data loader
    loader = MultiMarketDataLoader()

    test_symbols = {
        'ashare': ['600519.SH', '000858.SZ'],
        'hk': ['0700.HK'],
        'us': ['AAPL']
    }

    print("Testing MultiMarketDataLoader...")
    data = loader.load_data(test_symbols, '2024-01-01', '2024-06-30', 'daily')

    for symbol, df in data.items():
        print(f"\n{symbol}:")
        print(df.head())
        print(f"Shape: {df.shape}")
