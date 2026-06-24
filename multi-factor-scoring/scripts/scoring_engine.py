"""
Multi-Factor Scoring Engine
Calculates composite scores based on 6 factor categories
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

try:
    import ta
    TA_AVAILABLE = True
except ImportError:
    TA_AVAILABLE = False
    print("Warning: ta library not installed. Technical indicators will use simplified calculations.")

from config import *


class MultiFactorScorer:
    """Calculate multi-factor scores for stocks"""

    def __init__(self, factor_weights=None):
        """
        Initialize scorer with factor weights

        Args:
            factor_weights: Dict with keys ['momentum', 'technical', 'volume', 'fundamental', 'macro', 'sector']
        """
        if factor_weights is None:
            self.factor_weights = FACTOR_WEIGHTS
        else:
            # Validate weights sum to 1.0
            total = sum(factor_weights.values())
            if abs(total - 1.0) > 0.001:
                print(f"Warning: Factor weights sum to {total}, normalizing to 1.0")
                self.factor_weights = {k: v/total for k, v in factor_weights.items()}
            else:
                self.factor_weights = factor_weights

        print(f"Factor weights: {self.factor_weights}")

    def calculate_scores(self, data, fundamentals=None, macro_data=None):
        """
        Calculate composite scores for all symbols in data

        Args:
            data: Dict {symbol: DataFrame with OHLCV}
            fundamentals: Dict {symbol: dict with fundamental metrics}
            macro_data: Dict with macro indicators

        Returns:
            DataFrame: Index = symbols, columns = factor scores + composite score
        """
        scores = {}

        for symbol, df in data.items():
            if df is None or df.empty or len(df) < 50:
                print(f"Skipping {symbol}: insufficient data")
                continue

            # Calculate each factor score
            momentum_score = self._calculate_momentum_score(df)
            technical_score = self._calculate_technical_score(df)
            volume_score = self._calculate_volume_score(df)
            fundamental_score = self._calculate_fundamental_score(symbol, fundamentals)
            macro_score = self._calculate_macro_score(macro_data)
            sector_score = self._calculate_sector_score(symbol, data)

            # Store individual scores
            scores[symbol] = {
                'momentum': momentum_score,
                'technical': technical_score,
                'volume': volume_score,
                'fundamental': fundamental_score,
                'macro': macro_score,
                'sector': sector_score
            }

            # Calculate weighted composite score
            composite = (
                momentum_score * self.factor_weights['momentum'] +
                technical_score * self.factor_weights['technical'] +
                volume_score * self.factor_weights['volume'] +
                fundamental_score * self.factor_weights['fundamental'] +
                macro_score * self.factor_weights['macro'] +
                sector_score * self.factor_weights['sector']
            )

            scores[symbol]['composite'] = round(composite, 2)

        # Convert to DataFrame
        scores_df = pd.DataFrame.from_dict(scores, orient='index')

        return scores_df

    def _calculate_momentum_score(self, df, periods=MOMENTUM_PERIODS):
        """Calculate momentum factor score (0-100)"""
        try:
            close = df['close']

            # Calculate returns over multiple periods
            returns = {}
            for period in periods:
                if len(close) > period:
                    ret = (close.iloc[-1] / close.iloc[-period] - 1) * 100
                    returns[period] = ret
                else:
                    returns[period] = 0

            # Risk-adjusted momentum (return / volatility)
            volatility = close.pct_change().rolling(20).std().iloc[-1] * np.sqrt(252)
            if volatility > 0:
                recent_return = returns[periods[0]]
                risk_adj_momentum = recent_return / (volatility * 100)
            else:
                risk_adj_momentum = 0

            # Normalize to 0-100 scale
            # Assume momentum ranges from -50% to +50%
            momentum_raw = (
                0.5 * returns.get(periods[0], 0) +  # 1-month return
                0.3 * returns.get(periods[1], 0) +  # 3-month return
                0.2 * returns.get(periods[2], 0)     # 6-month return
            )

            # Clip and normalize
            momentum_raw = np.clip(momentum_raw, -50, 50)
            score = (momentum_raw + 50) * 1.0  # Convert -50~50 to 0~100

            return round(score, 2)

        except Exception as e:
            print(f"Error calculating momentum score: {e}")
            return 50.0  # Neutral score on error

    def _calculate_technical_score(self, df):
        """Calculate technical indicators score (0-100)"""
        try:
            if not TA_AVAILABLE:
                # Simplified technical score without ta library
                return self._calculate_simple_technical_score(df)

            close = df['close']
            high = df['high']
            low = df['low']

            score_components = []

            # RSI (14)
            rsi_indicator = ta.momentum.RSIIndicator(close=close, window=RSI_PERIOD)
            rsi = rsi_indicator.rsi().iloc[-1]
            # RSI: lower = better buy opportunity (oversold)
            # Convert: RSI < 30 = 80+ score, RSI > 70 = 20- score
            if rsi < 30:
                rsi_score = 80 + (30 - rsi) * 2.67  # Max 100
            elif rsi > 70:
                rsi_score = 20 - (rsi - 70) * 2.67  # Min 0
            else:
                rsi_score = 50
            score_components.append(rsi_score)

            # MACD
            macd_indicator = ta.trend.MACD(
                close=close,
                window_slow=MACD_PARAMS[1],
                window_fast=MACD_PARAMS[0],
                window_sign=MACD_PARAMS[2]
            )
            macd = macd_indicator.macd().iloc[-1]
            macd_signal = macd_indicator.macd_signal().iloc[-1]
            # MACD > Signal = bullish
            macd_diff = macd - macd_signal
            macd_score = 50 + macd_diff * 10  # Arbitrary scaling
            macd_score = np.clip(macd_score, 0, 100)
            score_components.append(macd_score)

            # Bollinger Bands
            bb_indicator = ta.volatility.BollingerBands(
                close=close,
                window=BOLLINGER_PERIOD,
                window_dev=BOLLINGER_STD
            )
            bb_upper = bb_indicator.bollinger_hband().iloc[-1]
            bb_lower = bb_indicator.bollinger_lband().iloc[-1]
            current_price = close.iloc[-1]

            # Price relative to Bollinger Bands
            bb_position = (current_price - bb_lower) / (bb_upper - bb_lower) if bb_upper > bb_lower else 0.5
            # Lower band = buy opportunity
            bb_score = (1 - bb_position) * 100
            score_components.append(bb_score)

            # Moving Average Trend
            ma20 = close.rolling(20).mean().iloc[-1]
            ma60 = close.rolling(60).mean().iloc[-1]
            current_price = close.iloc[-1]

            # Score based on MA alignment
            if current_price > ma20 > ma60:
                ma_score = 80  # Strong uptrend
            elif current_price > ma20:
                ma_score = 60  # Moderate uptrend
            elif current_price < ma20 < ma60:
                ma_score = 20  # Strong downtrend
            else:
                ma_score = 40  # Moderate downtrend
            score_components.append(ma_score)

            # Average all technical components
            final_score = np.mean(score_components)
            return round(final_score, 2)

        except Exception as e:
            print(f"Error calculating technical score: {e}")
            return 50.0

    def _calculate_simple_technical_score(self, df):
        """Simplified technical score without ta library"""
        try:
            close = df['close']

            # Simple RSI calculation
            delta = close.diff()
            gain = delta.where(delta > 0, 0).rolling(window=RSI_PERIOD).mean()
            loss = -delta.where(delta < 0, 0).rolling(window=RSI_PERIOD).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            rsi = rsi.iloc[-1]

            if rsi < 30:
                rsi_score = 80
            elif rsi > 70:
                rsi_score = 20
            else:
                rsi_score = 50

            # Simple MA score
            ma20 = close.rolling(20).mean().iloc[-1]
            current_price = close.iloc[-1]

            if current_price > ma20:
                ma_score = 65
            else:
                ma_score = 35

            return round((rsi_score + ma_score) / 2, 2)

        except Exception as e:
            print(f"Error in simple technical score: {e}")
            return 50.0

    def _calculate_volume_score(self, df):
        """Calculate volume-based score (0-100)"""
        try:
            close = df['close']
            volume = df['volume']

            # Volume change vs 20-day average
            vol_ma20 = volume.rolling(20).mean()
            vol_change = (volume.iloc[-1] / vol_ma20.iloc[-1] - 1) * 100

            # Price change
            price_change = (close.iloc[-1] / close.iloc[-2] - 1) * 100

            # Volume-price divergence analysis
            # Ideal: price up + volume up = bullish (high score)
            # Bad: price up + volume down = bearish (low score)
            if price_change > 0 and vol_change > 0:
                divergence_score = 80  # Bullish
            elif price_change > 0 and vol_change < 0:
                divergence_score = 30  # Bearish divergence
            elif price_change < 0 and vol_change > 0:
                divergence_score = 60  # Capitulation (could be bottom)
            else:
                divergence_score = 40  # Both down

            # Volume trend score (increasing volume = higher score)
            recent_vol = volume.tail(5).mean()
            older_vol = volume.tail(20).head(15).mean()
            vol_trend = (recent_vol / older_vol - 1) * 100

            vol_trend_score = np.clip(vol_trend + 50, 0, 100)

            # Combine scores
            final_score = 0.6 * divergence_score + 0.4 * vol_trend_score
            return round(final_score, 2)

        except Exception as e:
            print(f"Error calculating volume score: {e}")
            return 50.0

    def _calculate_fundamental_score(self, symbol, fundamentals):
        """Calculate fundamental factor score (0-100)"""
        try:
            if fundamentals is None or symbol not in fundamentals:
                # Use sample data from config
                if symbol in FUNDAMENTAL_DATA:
                    fund = FUNDAMENTAL_DATA[symbol]
                else:
                    return 50.0  # Neutral if no data
            else:
                fund = fundamentals[symbol]

            score_components = []

            # P/E ratio (lower = better, but not too low)
            pe = fund.get('pe', 20)
            if 5 < pe < 15:
                pe_score = 80  # Ideal range
            elif 15 <= pe < 25:
                pe_score = 60
            elif 25 <= pe < 35:
                pe_score = 40
            else:
                pe_score = 20
            score_components.append(pe_score)

            # P/B ratio (lower = better)
            pb = fund.get('pb', 2)
            if pb < 1.5:
                pb_score = 80
            elif pb < 3:
                pb_score = 60
            elif pb < 5:
                pb_score = 40
            else:
                pb_score = 20
            score_components.append(pb_score)

            # ROE (higher = better)
            roe = fund.get('roe', 0.15)
            roe_score = np.clip(roe * 300, 0, 100)  # ROE 33% = 100 score
            score_components.append(roe_score)

            # Revenue growth (higher = better)
            growth = fund.get('revenue_growth', 0.10)
            growth_score = np.clip(growth * 400, 0, 100)  # 25% growth = 100 score
            score_components.append(growth_score)

            final_score = np.mean(score_components)
            return round(final_score, 2)

        except Exception as e:
            print(f"Error calculating fundamental score for {symbol}: {e}")
            return 50.0

    def _calculate_macro_score(self, macro_data):
        """Calculate macro economic factor score (0-100)"""
        try:
            if macro_data is None:
                macro_data = MACRO_DATA

            score_components = []

            # Interest rate (lower = better for stocks)
            rate = macro_data.get('interest_rate', 0.0325)
            if rate < 0.02:
                rate_score = 80
            elif rate < 0.04:
                rate_score = 60
            elif rate < 0.06:
                rate_score = 40
            else:
                rate_score = 20
            score_components.append(rate_score)

            # CPI inflation (moderate = better)
            cpi = macro_data.get('cpi', 0.02)
            if 0.01 < cpi < 0.03:
                cpi_score = 70
            elif cpi < 0.01:
                cpi_score = 40  # Deflation risk
            else:
                cpi_score = 30  # High inflation
            score_components.append(cpi_score)

            # PMI (above 50 = expansion)
            pmi = macro_data.get('pmi', 50.5)
            pmi_score = np.clip((pmi - 40) * 10, 0, 100)  # PMI 50 = 100, PMI 40 = 0
            score_components.append(pmi_score)

            # GDP growth (higher = better)
            gdp = macro_data.get('gdp_growth', 0.052)
            gdp_score = np.clip(gdp * 1500, 0, 100)  # 6.7% GDP = 100 score
            score_components.append(gdp_score)

            final_score = np.mean(score_components)
            return round(final_score, 2)

        except Exception as e:
            print(f"Error calculating macro score: {e}")
            return 50.0

    def _calculate_sector_score(self, symbol, all_data):
        """Calculate sector/industry factor score (0-100)"""
        try:
            # Get sector for this symbol
            sector = SECTOR_MAP.get(symbol, 'unknown')

            # Calculate sector performance (average return of all stocks in sector)
            sector_returns = []
            for sym, df in all_data.items():
                if SECTOR_MAP.get(sym) == sector and df is not None and len(df) > 20:
                    ret = (df['close'].iloc[-1] / df['close'].iloc[-20] - 1) * 100
                    sector_returns.append(ret)

            if len(sector_returns) == 0:
                return 50.0

            # Sector relative strength vs market
            sector_avg_return = np.mean(sector_returns)

            # Normalize: assume sector return ranges from -20% to +20%
            sector_score = np.clip((sector_avg_return + 20) * 2.5, 0, 100)
            return round(sector_score, 2)

        except Exception as e:
            print(f"Error calculating sector score for {symbol}: {e}")
            return 50.0


if __name__ == "__main__":
    # Test the scorer
    from data_loader import MultiMarketDataLoader

    print("Testing MultiFactorScorer...")
    loader = MultiMarketDataLoader()
    data = loader.load_data(
        {'ashare': ['600519.SH', '000858.SZ']},
        '2024-01-01', '2024-06-30'
    )

    scorer = MultiFactorScorer()
    fundamentals = loader.load_fundamental_data(list(data.keys()))
    macro = loader.load_macro_data()

    scores = scorer.calculate_scores(data, fundamentals, macro)
    print("\nScoring Results:")
    print(scores)
