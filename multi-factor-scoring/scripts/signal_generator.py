"""
Signal Generator
Generates buy/sell signals based on dynamic thresholds of composite scores
"""

import pandas as pd
import numpy as np
from datetime import datetime


# Import configuration (MUST be before class definition)
try:
    from config import *
except ImportError:
    print("Warning: config.py not found. Using default values.")


class SignalGenerator:
    """Generate trading signals based on multi-factor scores"""

    def __init__(self,
                 buy_threshold_percentile=BUY_THRESHOLD_PERCENTILE,
                 sell_threshold_percentile=SELL_THRESHOLD_PERCENTILE,
                 score_improvement_threshold=SCORE_IMPROVEMENT_THRESHOLD,
                 score_decline_threshold=SCORE_DECLINE_THRESHOLD,
                 min_score_for_buy=MIN_SCORE_FOR_BUY,
                 max_score_for_sell=MAX_SCORE_FOR_SELL):
        """
        Initialize signal generator

        Args:
            buy_threshold_percentile: Buy when score is above this percentile (default 80)
            sell_threshold_percentile: Sell when score is below this percentile (default 20)
            score_improvement_threshold: Buy if score improves by this many points (default 20)
            score_decline_threshold: Sell if score declines by this many points (default 20)
            min_score_for_buy: Minimum composite score to hold a position (default 70)
            max_score_for_sell: Maximum composite score to sell (default 30)
        """
        self.buy_pct = buy_threshold_percentile
        self.sell_pct = sell_threshold_percentile
        self.improvement_thresh = score_improvement_threshold
        self.decline_thresh = score_decline_threshold
        self.min_score_buy = min_score_for_buy
        self.max_score_sell = max_score_for_sell

        print(f"Signal Generator initialized:")
        print(f"  Buy threshold: {self.buy_pct}th percentile")
        print(f"  Sell threshold: {self.sell_pct}th percentile")
        print(f"  Score improvement threshold: +{self.improvement_thresh} points")
        print(f"  Score decline threshold: -{self.decline_thresh} points")

    def generate_signals(self, current_scores, historical_scores=None, positions=None):
        """
        Generate trading signals based on current and historical scores

        Args:
            current_scores: DataFrame with current scores (from MultiFactorScorer)
            historical_scores: DataFrame with previous period scores (optional)
            positions: Dict of current positions {symbol: quantity}

        Returns:
            DataFrame: Trading signals with columns ['symbol', 'current_score', 'signal', 'reason']
                     signal: 'BUY', 'SELL', 'HOLD'
        """
        if current_scores is None or current_scores.empty:
            print("No scores provided!")
            return pd.DataFrame()

        # Calculate dynamic thresholds based on score distribution
        composite_scores = current_scores['composite']
        buy_threshold = np.percentile(composite_scores, self.buy_pct)
        sell_threshold = np.percentile(composite_scores, self.sell_pct)

        print(f"\nDynamic Thresholds:")
        print(f"  Buy threshold (>{self.buy_pct}th percentile): {buy_threshold:.2f}")
        print(f"  Sell threshold (<{self.sell_pct}th percentile): {sell_threshold:.2f}")

        signals = []

        for symbol in current_scores.index:
            current_score = current_scores.loc[symbol, 'composite']
            signal = 'HOLD'
            reason = ''

            # Check if we have historical scores
            if historical_scores is not None and symbol in historical_scores.index:
                prev_score = historical_scores.loc[symbol, 'composite']
                score_change = current_score - prev_score
            else:
                prev_score = None
                score_change = 0

            # Determine signal
            # BUY signals
            if current_score >= buy_threshold and current_score >= self.min_score_buy:
                signal = 'BUY'
                reason = f'Score {current_score:.1f} >= buy threshold {buy_threshold:.1f}'
            elif score_change >= self.improvement_thresh and current_score >= self.min_score_buy:
                signal = 'BUY'
                reason = f'Score improved by {score_change:.1f} points (>= {self.improvement_thresh})'
            elif current_score >= self.min_score_buy and prev_score is not None and prev_score < sell_threshold:
                # Recovery: was below sell threshold, now above min score
                signal = 'BUY'
                reason = f'Score recovered to {current_score:.1f} (was {prev_score:.1f})'

            # SELL signals (override BUY if both conditions met)
            if current_score <= sell_threshold or current_score <= self.max_score_sell:
                signal = 'SELL'
                reason = f'Score {current_score:.1f} <= sell threshold {sell_threshold:.1f}'
            elif score_change <= -self.decline_thresh:
                signal = 'SELL'
                reason = f'Score declined by {abs(score_change):.1f} points (>= {self.decline_thresh})'
            elif prev_score is not None and prev_score >= buy_threshold and current_score < self.min_score_buy:
                # Deterioration: was above buy threshold, now below min score
                signal = 'SELL'
                reason = f'Score deteriorated to {current_score:.1f} (was {prev_score:.1f})'

            # If position exists, might be HOLD even with BUY/SELL signal
            if positions is not None:
                if symbol in positions and positions[symbol] > 0:
                    # Already have position
                    if signal == 'BUY':
                        signal = 'HOLD'  # Keep existing position
                        reason = f'Already holding, score {current_score:.1f} still strong'
                    elif signal == 'SELL':
                        signal = 'SELL'  # Sell existing position
                        # reason already set

            signals.append({
                'symbol': symbol,
                'current_score': current_score,
                'prev_score': prev_score,
                'score_change': score_change,
                'signal': signal,
                'reason': reason
            })

        signals_df = pd.DataFrame(signals)
        signals_df = signals_df.sort_values('current_score', ascending=False)

        # Print summary
        self._print_signal_summary(signals_df)

        return signals_df

    def calculate_position_size(self, score, max_position_size=MAX_POSITION_SIZE):
        """
        Calculate position size based on composite score

        Formula: (Score - 50) / 50 * Max_Position_Size
        Score 100 = 100% of max position
        Score 50 = 0% of max position
        Score 0 = -100% of max position (short, if allowed)

        Args:
            score: Composite score (0-100)
            max_position_size: Maximum position size as fraction of portfolio (e.g., 0.10 = 10%)

        Returns:
            float: Position size as fraction of portfolio (0-1)
        """
        if score <= 50:
            return 0.0  # Don't buy if score <= 50

        position_fraction = (score - 50) / 50 * max_position_size
        position_fraction = min(position_fraction, max_position_size)  # Cap at max

        return round(position_fraction, 4)

    def generate_signals_with_position_sizing(self, current_scores, historical_scores=None, portfolio_value=100000):
        """
        Generate signals with recommended position sizes

        Args:
            current_scores: DataFrame with current scores
            historical_scores: DataFrame with previous period scores
            portfolio_value: Total portfolio value for position sizing

        Returns:
            DataFrame: Signals with position size recommendations
        """
        signals = self.generate_signals(current_scores, historical_scores)

        # Add position size recommendations
        signals['recommended_position_pct'] = signals['current_score'].apply(
            lambda s: self.calculate_position_size(s)
        )

        signals['recommended_position_value'] = signals['recommended_position_pct'] * portfolio_value

        return signals

    def _print_signal_summary(self, signals_df):
        """Print summary of generated signals"""
        print(f"\n=== Signal Summary ===")
        print(f"Total stocks analyzed: {len(signals_df)}")
        print(f"BUY signals: {len(signals_df[signals_df['signal'] == 'BUY'])}")
        print(f"SELL signals: {len(signals_df[signals_df['signal'] == 'SELL'])}")
        print(f"HOLD signals: {len(signals_df[signals_df['signal'] == 'HOLD'])}")

        # Top 5 stocks by score
        print(f"\nTop 5 stocks by composite score:")
        top5 = signals_df.head(5)[['symbol', 'current_score', 'signal']]
        for _, row in top5.iterrows():
            print(f"  {row['symbol']}: {row['current_score']:.1f} - {row['signal']}")

        # Bottom 5 stocks by score
        print(f"\nBottom 5 stocks by composite score:")
        bot5 = signals_df.tail(5)[['symbol', 'current_score', 'signal']]
        for _, row in bot5.iterrows():
            print(f"  {row['symbol']}: {row['current_score']:.1f} - {row['signal']}")


if __name__ == "__main__":
    # Test the signal generator
    from scoring_engine import MultiFactorScorer
    from data_loader import MultiMarketDataLoader

    print("Testing SignalGenerator...")

    # Load data and calculate scores
    loader = MultiMarketDataLoader()
    data = loader.load_data(
        {'ashare': ['600519.SH', '000858.SZ', '601318.SH']},
        '2024-01-01', '2024-06-30'
    )

    scorer = MultiFactorScorer()
    fundamentals = loader.load_fundamental_data(list(data.keys()))
    macro = loader.load_macro_data()

    current_scores = scorer.calculate_scores(data, fundamentals, macro)

    # Generate signals
    generator = SignalGenerator()
    signals = generator.generate_signals_with_position_sizing(
        current_scores,
        portfolio_value=100000
    )

    print("\nDetailed Signals:")
    print(signals.to_string(index=False))
