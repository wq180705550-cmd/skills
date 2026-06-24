"""
Backtest Engine
Backtest multi-factor scoring strategy with historical data
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')


class BacktestEngine:
    """Backtest engine for multi-factor scoring strategy"""

    def __init__(self,
                 initial_capital=INITIAL_CAPITAL,
                 commission=COMMISSION,
                 slippage=SLIPPAGE,
                 stop_loss=STOP_LOSS,
                 take_profit=TAKE_PROFIT,
                 max_position_size=MAX_POSITION_SIZE):
        """
        Initialize backtest engine

        Args:
            initial_capital: Starting capital
            commission: Trading commission (e.g., 0.0003 = 0.03%)
            slippage: Slippage per trade (e.g., 0.001 = 0.1%)
            stop_loss: Stop loss percentage (e.g., 0.08 = 8%)
            take_profit: Take profit percentage (e.g., 0.20 = 20%)
            max_position_size: Maximum position size per stock (e.g., 0.10 = 10%)
        """
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.max_position_size = max_position_size

        self.portfolio_value = []
        self.positions = {}  # {symbol: {'quantity': int, 'cost_basis': float}}
        self.trades = []  # List of trade records
        self.cash = initial_capital

        print(f"Backtest Engine initialized:")
        print(f"  Initial Capital: {initial_capital:,.0f}")
        print(f"  Commission: {commission*100:.3f}%")
        print(f"  Slippage: {slippage*100:.3f}%")
        print(f"  Stop Loss: {stop_loss*100:.1f}%")
        print(f"  Take Profit: {take_profit*100:.1f}%")

    def run_backtest(self, data, signals_df, dates=None):
        """
        Run backtest on historical data

        Args:
            data: Dict {symbol: DataFrame with OHLCV}
            signals_df: DataFrame with signals (must have 'symbol' and 'signal' columns)
            dates: List of dates to run backtest (if None, use all dates in data)

        Returns:
            dict: Backtest results
        """
        print(f"\n{'='*60}")
        print(f"Starting Backtest...")
        print(f"{'='*60}")

        # Get all trading dates
        if dates is None:
            # Use dates from the first symbol
            first_symbol = list(data.keys())[0]
            dates = data[first_symbol].index.tolist()

        print(f"Total trading days: {len(dates)}")
        print(f"Universe size: {len(data)} stocks")

        # Run day by day
        for i, date in enumerate(dates):
            if i % 20 == 0:
                print(f"Progress: {i}/{len(dates)} days ({i/len(dates)*100:.1f}%)")

            self._process_date(data, signals_df, date)

            # Record portfolio value
            portfolio_value = self._calculate_portfolio_value(data, date)
            self.portfolio_value.append({
                'date': date,
                'value': portfolio_value,
                'cash': self.cash
            })

        # Calculate final results
        results = self._calculate_results()
        return results

    def _process_date(self, data, signals_df, date):
        """Process a single trading date"""
        # Get signals for this date (in practice, signals would be date-specific)
        # For now, use the same signals for all dates (simplified)
        for _, row in signals_df.iterrows():
            symbol = row['symbol']
            signal = row['signal']

            if symbol not in data or date not in data[symbol].index:
                continue

            current_price = data[symbol].loc[date, 'close']

            # Execute signal
            if signal == 'BUY' and (symbol not in self.positions or self.positions[symbol]['quantity'] == 0):
                self._execute_buy(symbol, current_price, date, row['current_score'])
            elif signal == 'SELL' and symbol in self.positions and self.positions[symbol]['quantity'] > 0:
                self._execute_sell(symbol, current_price, date, row['current_score'])

            # Check stop loss / take profit
            if symbol in self.positions and self.positions[symbol]['quantity'] > 0:
                self._check_stop_loss_take_profit(symbol, current_price, date)

    def _execute_buy(self, symbol, price, date, score):
        """Execute buy order"""
        # Calculate position size based on score
        from signal_generator import SignalGenerator
        generator = SignalGenerator()
        position_pct = generator.calculate_position_size(score, self.max_position_size)

        if position_pct <= 0:
            return

        # Calculate number of shares
        position_value = self.cash * position_pct  # Use available cash
        actual_position_value = min(position_value, self.cash * self.max_position_size)

        # Apply slippage and commission
        execution_price = price * (1 + self.slippage)
        total_cost = actual_position_value * (1 + self.commission)

        if total_cost > self.cash:
            # Not enough cash
            actual_position_value = self.cash / (1 + self.commission)
            total_cost = actual_position_value * (1 + self.commission)
            execution_price = price * (1 + self.slippage)
            quantity = int(actual_position_value / execution_price)
        else:
            quantity = int(actual_position_value / execution_price)

        if quantity <= 0:
            return

        # Update positions and cash
        self.positions[symbol] = {
            'quantity': quantity,
            'cost_basis': execution_price,
            'entry_date': date
        }
        self.cash -= (quantity * execution_price + quantity * execution_price * self.commission)

        # Record trade
        self.trades.append({
            'date': date,
            'symbol': symbol,
            'action': 'BUY',
            'quantity': quantity,
            'price': execution_price,
            'value': quantity * execution_price,
            'commission': quantity * execution_price * self.commission,
            'score': score
        })

        print(f"{date.strftime('%Y-%m-%d')}: BUY {quantity} shares of {symbol} @ {execution_price:.2f} (Score: {score:.1f})")

    def _execute_sell(self, symbol, price, date, score):
        """Execute sell order"""
        if symbol not in self.positions or self.positions[symbol]['quantity'] == 0:
            return

        position = self.positions[symbol]
        quantity = position['quantity']

        # Apply slippage and commission
        execution_price = price * (1 - self.slippage)
        proceeds = quantity * execution_price * (1 - self.commission)

        # Update cash and positions
        self.cash += proceeds
        self.positions[symbol] = {'quantity': 0, 'cost_basis': 0, 'entry_date': None}

        # Calculate P&L
        cost = quantity * position['cost_basis']
        pnl = proceeds - cost
        pnl_pct = (execution_price / position['cost_basis'] - 1) * 100

        # Record trade
        self.trades.append({
            'date': date,
            'symbol': symbol,
            'action': 'SELL',
            'quantity': quantity,
            'price': execution_price,
            'value': quantity * execution_price,
            'commission': quantity * execution_price * self.commission,
            'pnl': pnl,
            'pnl_pct': pnl_pct,
            'score': score
        })

        print(f"{date.strftime('%Y-%m-%d')}: SELL {quantity} shares of {symbol} @ {execution_price:.2f} | P&L: {pnl:+.2f} ({pnl_pct:+.2f}%)")

    def _check_stop_loss_take_profit(self, symbol, price, date):
        """Check if stop loss or take profit triggered"""
        if symbol not in self.positions or self.positions[symbol]['quantity'] == 0:
            return

        position = self.positions[symbol]
        cost_basis = position['cost_basis']

        # Stop loss
        if price <= cost_basis * (1 - self.stop_loss):
            print(f"Stop Loss triggered for {symbol} @ {price:.2f}")
            self._execute_sell(symbol, price, date, 0)  # Score=0 for stop loss

        # Take profit
        elif price >= cost_basis * (1 + self.take_profit):
            print(f"Take Profit triggered for {symbol} @ {price:.2f}")
            self._execute_sell(symbol, price, date, 100)  # Score=100 for take profit

    def _calculate_portfolio_value(self, data, date):
        """Calculate total portfolio value"""
        total_value = self.cash

        for symbol, position in self.positions.items():
            if position['quantity'] > 0 and symbol in data and date in data[symbol].index:
                current_price = data[symbol].loc[date, 'close']
                total_value += position['quantity'] * current_price

        return total_value

    def _calculate_results(self):
        """Calculate backtest performance metrics"""
        if len(self.portfolio_value) == 0:
            return {}

        # Convert to DataFrame
        df = pd.DataFrame(self.portfolio_value)
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)

        # Calculate returns
        df['returns'] = df['value'].pct_change()
        df['cumulative_returns'] = (1 + df['returns']).cumprod() - 1

        # Performance metrics
        total_return = (df['value'].iloc[-1] / self.initial_capital - 1) * 100
        annualized_return = (df['value'].iloc[-1] / self.initial_capital) ** (252 / len(df)) - 1
        annualized_return *= 100

        # Sharpe ratio (assuming risk-free rate = 2%)
        risk_free_rate = 0.02 / 252  # Daily risk-free rate
        excess_returns = df['returns'] - risk_free_rate
        sharpe_ratio = np.sqrt(252) * excess_returns.mean() / excess_returns.std()

        # Maximum drawdown
        df['cummax'] = df['value'].cummax()
        df['drawdown'] = (df['value'] - df['cummax']) / df['cummax']
        max_drawdown = df['drawdown'].min() * 100

        # Win rate
        if len(self.trades) > 0:
            trades_df = pd.DataFrame(self.trades)
            sell_trades = trades_df[trades_df['action'] == 'SELL']
            if len(sell_trades) > 0:
                winning_trades = sell_trades[sell_trades['pnl'] > 0]
                win_rate = len(winning_trades) / len(sell_trades) * 100
            else:
                win_rate = 0
        else:
            win_rate = 0

        results = {
            'initial_capital': self.initial_capital,
            'final_value': df['value'].iloc[-1],
            'total_return': total_return,
            'annualized_return': annualized_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'num_trades': len(self.trades),
            'portfolio_df': df
        }

        return results

    def print_results(self, results):
        """Print backtest results"""
        print(f"\n{'='*60}")
        print(f"Backtest Results")
        print(f"{'='*60}")
        print(f"Initial Capital: {results['initial_capital']:,.0f}")
        print(f"Final Value: {results['final_value']:,.2f}")
        print(f"Total Return: {results['total_return']:.2f}%")
        print(f"Annualized Return: {results['annualized_return']:.2f}%")
        print(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")
        print(f"Maximum Drawdown: {results['max_drawdown']:.2f}%")
        print(f"Win Rate: {results['win_rate']:.2f}%")
        print(f"Number of Trades: {results['num_trades']}")

    def plot_results(self, results, save_path='backtest_results.png'):
        """Plot backtest results"""
        df = results['portfolio_df']

        fig, axes = plt.subplots(2, 1, figsize=(14, 10))

        # Plot 1: Portfolio Value
        ax1 = axes[0]
        ax1.plot(df.index, df['value'], label='Portfolio Value', linewidth=2)
        ax1.axhline(y=self.initial_capital, color='r', linestyle='--', label='Initial Capital')
        ax1.set_ylabel('Portfolio Value', fontsize=12)
        ax1.set_title('Backtest Results - Portfolio Value Over Time', fontsize=14)
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Plot 2: Cumulative Returns
        ax2 = axes[1]
        ax2.plot(df.index, df['cumulative_returns'] * 100, label='Cumulative Returns (%)', linewidth=2)
        ax2.set_ylabel('Cumulative Returns (%)', fontsize=12)
        ax2.set_xlabel('Date', fontsize=12)
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(save_path, dpi=100, bbox_inches='tight')
        print(f"\nPlot saved to: {save_path}")
        plt.show()


if __name__ == "__main__":
    # Test the backtest engine
    from data_loader import MultiMarketDataLoader
    from scoring_engine import MultiFactorScorer
    from signal_generator import SignalGenerator

    print("Testing BacktestEngine...")

    # Load data
    loader = MultiMarketDataLoader()
    data = loader.load_data(
        {'ashare': ['600519.SH', '000858.SZ', '601318.SH']},
        '2024-01-01', '2024-06-30'
    )

    # Calculate scores
    scorer = MultiFactorScorer()
    fundamentals = loader.load_fundamental_data(list(data.keys()))
    macro = loader.load_macro_data()
    scores = scorer.calculate_scores(data, fundamentals, macro)

    # Generate signals
    generator = SignalGenerator()
    signals = generator.generate_signals(scores)

    # Run backtest
    engine = BacktestEngine(initial_capital=100000)
    results = engine.run_backtest(data, signals)

    # Print results
    engine.print_results(results)

    # Plot results
    engine.plot_results(results)
