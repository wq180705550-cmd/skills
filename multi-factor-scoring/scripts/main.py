"""
Main Execution Script for Multi-Factor Scoring Quantitative Trading System
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import sys

# Import modules
from data_loader import MultiMarketDataLoader
from scoring_engine import MultiFactorScorer
from signal_generator import SignalGenerator
from backtest import BacktestEngine
from simulated_broker import SimulatedBroker
from visualization import Visualizer
from config import *


class MultiFactorTradingSystem:
    """Main system orchestrating all components"""

    def __init__(self, config_overrides=None):
        """
        Initialize the trading system

        Args:
            config_overrides: Dict to override config settings
        """
        print(f"\n{'='*60}")
        print(f"Multi-Factor Scoring Quantitative Trading System")
        print(f"{'='*60}\n")

        # Override config if provided
        if config_overrides:
            for key, value in config_overrides.items():
                globals()[key] = value
                print(f"Config override: {key} = {value}")

        # Initialize components
        self.data_loader = MultiMarketDataLoader(cache_dir=DATA_CACHE_DIR)
        self.scorer = MultiFactorScorer(factor_weights=FACTOR_WEIGHTS)
        self.signal_generator = SignalGenerator(
            buy_threshold_percentile=BUY_THRESHOLD_PERCENTILE,
            sell_threshold_percentile=SELL_THRESHOLD_PERCENTILE
        )
        self.visualizer = Visualizer()

        self.data = None
        self.fundamentals = None
        self.macro_data = None
        self.scores = None
        self.signals = None

        print(f"\nSystem initialized successfully!")

    def load_data(self, symbols=None, start_date=None, end_date=None, timeframe='daily'):
        """
        Load market data

        Args:
            symbols: Dict with keys 'ashare', 'hk', 'us' or list of symbols
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            timeframe: 'daily', '4h', '1h', '15m'
        """
        if symbols is None:
            symbols = SYMBOLS

        if start_date is None:
            start_date = DATA_START_DATE

        if end_date is None:
            end_date = DATA_END_DATE

        print(f"\n{'='*60}")
        print(f"Loading Market Data...")
        print(f"  Period: {start_date} to {end_date}")
        print(f"  Timeframe: {timeframe}")
        print(f"  Symbols: {self._count_symbols(symbols)} total")
        print(f"{'='*60}\n")

        self.data = self.data_loader.load_data(
            symbols, start_date, end_date, timeframe
        )

        print(f"\nData loaded successfully!")
        print(f"  Symbols loaded: {len(self.data)}")

        # Load fundamentals and macro data
        all_symbols = self._get_all_symbols(symbols)
        self.fundamentals = self.data_loader.load_fundamental_data(all_symbols)
        self.macro_data = self.data_loader.load_macro_data()

        return self.data

    def calculate_scores(self):
        """Calculate multi-factor scores"""
        if self.data is None:
            print("Error: No data loaded! Call load_data() first.")
            return None

        print(f"\n{'='*60}")
        print(f"Calculating Multi-Factor Scores...")
        print(f"{'='*60}\n")

        self.scores = self.scorer.calculate_scores(
            self.data, self.fundamentals, self.macro_data
        )

        print(f"\nScoring completed!")
        print(f"  Stocks scored: {len(self.scores)}")

        # Print top 5 and bottom 5
        sorted_scores = self.scores.sort_values('composite', ascending=False)
        print(f"\nTop 5 stocks by composite score:")
        print(sorted_scores[['composite']].head().to_string())

        print(f"\nBottom 5 stocks by composite score:")
        print(sorted_scores[['composite']].tail().to_string())

        return self.scores

    def generate_signals(self):
        """Generate trading signals"""
        if self.scores is None:
            print("Error: No scores calculated! Call calculate_scores() first.")
            return None

        print(f"\n{'='*60}")
        print(f"Generating Trading Signals...")
        print(f"{'='*60}\n")

        self.signals = self.signal_generator.generate_signals_with_position_sizing(
            self.scores,
            portfolio_value=INITIAL_CAPITAL
        )

        print(f"\nSignal generation completed!")

        return self.signals

    def run_backtest(self):
        """Run backtest on historical data"""
        if self.scores is None or self.signals is None:
            print("Error: Need scores and signals! Call calculate_scores() and generate_signals() first.")
            return None

        print(f"\n{'='*60}")
        print(f"Running Backtest...")
        print(f"{'='*60}\n")

        engine = BacktestEngine(
            initial_capital=INITIAL_CAPITAL,
            commission=COMMISSION,
            slippage=SLIPPAGE
        )

        results = engine.run_backtest(self.data, self.signals)
        engine.print_results(results)

        # Plot results
        engine.plot_results(results, save_path='backtest_results.png')

        return results

    def run_simulated_trading(self):
        """Run simulated trading"""
        if self.signals is None:
            print("Error: No signals generated! Call generate_signals() first.")
            return None

        print(f"\n{'='*60}")
        print(f"Running Simulated Trading...")
        print(f"{'='*60}\n")

        broker = SimulatedBroker(
            initial_capital=INITIAL_CAPITAL,
            commission=COMMISSION,
            slippage=SLIPPAGE
        )

        broker.execute_signals(self.signals, self.data)
        broker.print_portfolio_summary()
        broker.save_state('trading_state.json')

        return broker

    def visualize(self, scores=None, signals=None, portfolio_state=None):
        """
        Generate visualizations

        Args:
            scores: Scores DataFrame (if None, use self.scores)
            signals: Signals DataFrame (if None, use self.signals)
            portfolio_state: Portfolio state dict (if None, try to load from file)
        """
        if scores is None:
            scores = self.scores

        if scores is None:
            print("Error: No scores to visualize!")
            return

        print(f"\n{'='*60}")
        print(f"Generating Visualizations...")
        print(f"{'='*60}\n")

        # Plot 1: Scores Heatmap
        self.visualizer.plot_scores_heatmap(
            scores,
            title='Multi-Factor Scores Heatmap',
            save_path='scores_heatmap.png'
        )

        # Plot 2: Top/Bottom stocks
        self.visualizer.plot_top_bottom_stocks(
            scores,
            top_n=10,
            title='Top/Bottom 10 Stocks by Composite Score',
            save_path='top_bottom_stocks.png'
        )

        # Plot 3: Factor exposure
        self.visualizer.plot_factor_exposure(
            scores,
            title='Average Factor Exposure',
            save_path='factor_exposure.png'
        )

        # Plot 4: Portfolio composition (if available)
        if portfolio_state and 'positions' in portfolio_state:
            self.visualizer.plot_portfolio_composition(
                portfolio_state['positions'],
                title='Portfolio Composition',
                save_path='portfolio_composition.png'
            )

        print(f"\nAll visualizations saved!")

    def save_results(self, output_dir='output'):
        """Save all results to files"""
        os.makedirs(output_dir, exist_ok=True)

        print(f"\n{'='*60}")
        print(f"Saving Results to {output_dir}/...")
        print(f"{'='*60}\n")

        # Save scores
        if self.scores is not None:
            self.scores.to_csv(f"{output_dir}/scores.csv")
            print(f"  Scores saved to: {output_dir}/scores.csv")

        # Save signals
        if self.signals is not None:
            self.signals.to_csv(f"{output_dir}/signals.csv", index=False)
            print(f"  Signals saved to: {output_dir}/signals.csv")

        # Generate HTML report
        if self.scores is not None and self.signals is not None:
            portfolio_state = {'total_value': 0, 'cash': 0, 'positions_value': 0}
            self.visualizer.generate_html_report(
                self.scores, self.signals, portfolio_state,
                output_path=f"{output_dir}/report.html"
            )
            print(f"  HTML report saved to: {output_dir}/report.html")

        print(f"\nAll results saved successfully!")

    def run_full_pipeline(self, symbols=None, start_date=None, end_date=None, timeframe='daily'):
        """
        Run the full pipeline: load data → calculate scores → generate signals → backtest → visualize

        Args:
            symbols: Dict with keys 'ashare', 'hk', 'us'
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            timeframe: 'daily', '4h', '1h', '15m'

        Returns:
            dict: All results
        """
        print(f"\n{'#'*60}")
        print(f"# Running Full Pipeline")
        print(f"{'#'*60}\n")

        # Step 1: Load data
        self.load_data(symbols, start_date, end_date, timeframe)

        # Step 2: Calculate scores
        self.calculate_scores()

        # Step 3: Generate signals
        self.generate_signals()

        # Step 4: Run backtest
        backtest_results = self.run_backtest()

        # Step 5: Run simulated trading
        broker = self.run_simulated_trading()

        # Step 6: Visualize
        portfolio_state = broker.portfolio_history[-1] if len(broker.portfolio_history) > 0 else None
        self.visualize(scores=self.scores, signals=self.signals, portfolio_state=portfolio_state)

        # Step 7: Save results
        self.save_results()

        print(f"\n{'='*60}")
        print(f"Pipeline Completed Successfully!")
        print(f"{'='*60}\n")

        return {
            'scores': self.scores,
            'signals': self.signals,
            'backtest_results': backtest_results,
            'broker': broker
        }

    def _count_symbols(self, symbols):
        """Count total symbols"""
        if isinstance(symbols, dict):
            return sum(len(v) for v in symbols.values())
        elif isinstance(symbols, list):
            return len(symbols)
        else:
            return 0

    def _get_all_symbols(self, symbols):
        """Get all symbols as a flat list"""
        if isinstance(symbols, dict):
            all_symbols = []
            for market, syms in symbols.items():
                all_symbols.extend(syms)
            return all_symbols
        elif isinstance(symbols, list):
            return symbols
        else:
            return []


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Multi-Factor Scoring Quantitative Trading System')
    parser.add_argument('--mode', choices=['full', 'load', 'score', 'signal', 'backtest', 'trade', 'visualize'],
                        default='full', help='Run mode')
    parser.add_argument('--symbols', nargs='+', help='Stock symbols (overrides config)')
    parser.add_argument('--start', type=str, default=DATA_START_DATE, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end', type=str, default=DATA_END_DATE, help='End date (YYYY-MM-DD)')
    parser.add_argument('--timeframe', type=str, default='daily', help='Timeframe (daily/4h/1h/15m)')
    parser.add_argument('--initial-capital', type=float, default=INITIAL_CAPITAL, help='Initial capital')

    args = parser.parse_args()

    # Config overrides
    config_overrides = {}
    if args.initial_capital != INITIAL_CAPITAL:
        config_overrides['INITIAL_CAPITAL'] = args.initial_capital

    # Initialize system
    system = MultiFactorTradingSystem(config_overrides=config_overrides)

    # Run based on mode
    if args.mode == 'full':
        system.run_full_pipeline(
            start_date=args.start,
            end_date=args.end,
            timeframe=args.timeframe
        )
    elif args.mode == 'load':
        system.load_data(start_date=args.start, end_date=args.end, timeframe=args.timeframe)
    elif args.mode == 'score':
        system.load_data(start_date=args.start, end_date=args.end, timeframe=args.timeframe)
        system.calculate_scores()
    elif args.mode == 'signal':
        system.load_data(start_date=args.start, end_date=args.end, timeframe=args.timeframe)
        system.calculate_scores()
        system.generate_signals()
    elif args.mode == 'backtest':
        system.load_data(start_date=args.start, end_date=args.end, timeframe=args.timeframe)
        system.calculate_scores()
        system.generate_signals()
        system.run_backtest()
    elif args.mode == 'trade':
        system.load_data(start_date=args.start, end_date=args.end, timeframe=args.timeframe)
        system.calculate_scores()
        system.generate_signals()
        system.run_simulated_trading()
    elif args.mode == 'visualize':
        system.visualize()


if __name__ == "__main__":
    main()
