"""
Simulated Broker
Execute simulated trades based on signals
Incorporates dynamic transaction cost optimization (arXiv:2606.21784)
"""

import pandas as pd
import numpy as np
from datetime import datetime
import json
import os


# Import configuration
try:
    from config import *
except ImportError:
    print("Warning: config.py not found.")


class SimulatedBroker:
    """
    Simulated broker for paper trading.
    
    New features (2026 arXiv papers):
    - Dynamic transaction cost optimization (arXiv:2606.21784)
    - Market impact-based commission adjustment
    """
    
    def __init__(self, initial_capital=INITIAL_CAPITAL, commission=COMMISSION, slippage=SLIPPAGE, 
                 enable_dynamic_costs=True):
        """
        Initialize simulated broker
        
        Args:
            initial_capital: Starting capital
            commission: Base trading commission rate
            slippage: Base slippage rate
            enable_dynamic_costs: Enable dynamic transaction cost optimization (arXiv:2606.21784)
        """
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.base_commission = commission
        self.base_slippage = slippage
        self.enable_dynamic_costs = enable_dynamic_costs
        
        self.positions = {}  # {symbol: {'quantity': int, 'cost_basis': float, 'entry_date': date}}
        self.portfolio_history = []  # List of {date, value, cash, positions}
        self.trade_history = []  # List of trade records
        
        self.current_date = None
        
        print(f"Simulated Broker initialized:")
        print(f"  Initial Capital: {initial_capital:,.2f}")
        print(f"  Base Commission: {commission*100:.3f}%")
        print(f"  Base Slippage: {slippage*100:.3f}%")
        print(f"  Dynamic Costs: {'ON' if enable_dynamic_costs else 'OFF'}")

    def execute_signals(self, signals_df, data, date=None):
        """
        Execute buy/sell signals
        
        Args:
            signals_df: DataFrame with columns ['symbol', 'signal', 'current_score']
            data: Dict {symbol: DataFrame with OHLCV}
            date: Current date (if None, use latest date in data)
        """
        if date is None:
            # Get latest date from data
            all_dates = []
            for symbol, df in data.items():
                if df is not None and not df.empty:
                    all_dates.append(df.index[-1])
            if len(all_dates) > 0:
                date = max(all_dates)
            else:
                date = datetime.now()
        
        self.current_date = date
        print(f"\n{'='*60}")
        print(f"Executing Signals for {date.strftime('%Y-%m-%d')}")
        print(f"{'='*60}")
        
        # Process signals
        for _, row in signals_df.iterrows():
            symbol = row['symbol']
            signal = row['signal']
            score = row['current_score']
            
            if symbol not in data:
                continue
            
            # Get current price
            df = data[symbol]
            if date not in df.index:
                # Find closest date
                closest_idx = df.index.get_indexer([date], method='nearest')[0]
                current_price = df.iloc[closest_idx]['close']
            else:
                current_price = df.loc[date, 'close']
            
            # Execute signal (pass data for dynamic cost calculation)
            if signal == 'BUY':
                self._buy(symbol, current_price, score, date, data)
            elif signal == 'SELL':
                self._sell(symbol, current_price, score, date, data)
        
        # Record portfolio state
        self._record_portfolio_state(data, date)

    def _buy(self, symbol, price, score, date, data=None):
        """Execute buy order with dynamic cost optimization"""
        if symbol in self.positions and self.positions[symbol]['quantity'] > 0:
            # Already have position, might add (scale in)
            self._add_to_position(symbol, price, score, date, data)
            return
        
        # Calculate position size based on score
        from signal_generator import SignalGenerator
        generator = SignalGenerator()
        position_pct = generator.calculate_position_size(score, MAX_POSITION_SIZE)
        
        if position_pct <= 0:
            print(f"  {symbol}: Score {score:.1f} too low to buy (position_pct={position_pct:.2%})")
            return
        
        # Calculate quantity
        position_value = self.cash * position_pct
        
        # Use dynamic slippage
        if data is not None:
            dynamic_slippage = self._calculate_dynamic_slippage(symbol, int(position_value / price), price, data)
            execution_price = price * (1 + dynamic_slippage)
        else:
            execution_price = price * (1 + self.base_slippage)
        
        quantity = int(position_value / execution_price)
        
        if quantity <= 0:
            print(f"  {symbol}: Insufficient cash to buy (position_value={position_value:.2f})")
            return
        
        # Calculate dynamic commission
        if data is not None:
            dynamic_commission = self._calculate_dynamic_commission(symbol, quantity, execution_price, data)
        else:
            dynamic_commission = self.base_commission
        
        # Check if enough cash
        total_cost = quantity * execution_price * (1 + dynamic_commission)
        if total_cost > self.cash:
            # Reduce quantity
            quantity = int(self.cash / (execution_price * (1 + dynamic_commission)))
            if quantity <= 0:
                return
            total_cost = quantity * execution_price * (1 + dynamic_commission)
        
        # Execute buy
        self.cash -= total_cost
        self.positions[symbol] = {
            'quantity': quantity,
            'cost_basis': execution_price,
            'entry_date': date,
            'entry_score': score
        }
        
        # Record trade
        trade = {
            'date': date,
            'symbol': symbol,
            'action': 'BUY',
            'quantity': quantity,
            'price': execution_price,
            'value': quantity * execution_price,
            'commission': quantity * execution_price * dynamic_commission,
            'commission_rate': dynamic_commission,
            'slippage_rate': dynamic_slippage if data is not None else self.base_slippage,
            'score': score,
            'cash_after': self.cash
        }
        self.trade_history.append(trade)
        
        print(f"  BUY {symbol}: {quantity} shares @ {execution_price:.2f} | Score: {score:.1f} | Commission: {dynamic_commission*100:.3f}% | Cash left: {self.cash:,.2f}")

    def _add_to_position(self, symbol, price, score, date, data=None):
        """Add to existing position (scale in) with dynamic costs"""
        position = self.positions[symbol]
        
        # Only add if score improved
        if score <= position.get('entry_score', 50):
            return
        
        # Calculate additional position size
        from signal_generator import SignalGenerator
        generator = SignalGenerator()
        position_pct = generator.calculate_position_size(score, MAX_POSITION_SIZE)
        
        additional_value = self.cash * position_pct * 0.5  # Only use 50% of recommended for scaling in
        
        # Use dynamic slippage
        if data is not None:
            dynamic_slippage = self._calculate_dynamic_slippage(symbol, int(additional_value / price), price, data)
            execution_price = price * (1 + dynamic_slippage)
        else:
            execution_price = price * (1 + self.base_slippage)
        
        additional_quantity = int(additional_value / execution_price)
        
        if additional_quantity <= 0:
            return
        
        # Calculate dynamic commission
        if data is not None:
            dynamic_commission = self._calculate_dynamic_commission(symbol, additional_quantity, execution_price, data)
        else:
            dynamic_commission = self.base_commission
        
        # Check cash
        total_cost = additional_quantity * execution_price * (1 + dynamic_commission)
        if total_cost > self.cash:
            additional_quantity = int(self.cash / (execution_price * (1 + dynamic_commission)))
            if additional_quantity <= 0:
                return
            total_cost = additional_quantity * execution_price * (1 + dynamic_commission)
        
        # Update position (average cost basis)
        old_quantity = position['quantity']
        old_cost = position['cost_basis']
        new_quantity = old_quantity + additional_quantity
        new_cost_basis = (old_quantity * old_cost + additional_quantity * execution_price) / new_quantity
        
        self.cash -= total_cost
        self.positions[symbol] = {
            'quantity': new_quantity,
            'cost_basis': new_cost_basis,
            'entry_date': position['entry_date'],
            'entry_score': position['entry_score']
        }
        
        # Record trade
        trade = {
            'date': date,
            'symbol': symbol,
            'action': 'BUY_ADD',
            'quantity': additional_quantity,
            'price': execution_price,
            'value': additional_quantity * execution_price,
            'commission': additional_quantity * execution_price * dynamic_commission,
            'commission_rate': dynamic_commission,
            'score': score,
            'cash_after': self.cash
        }
        self.trade_history.append(trade)
        
        print(f"  ADD {symbol}: +{additional_quantity} shares @ {execution_price:.2f} | New avg cost: {new_cost_basis:.2f}")

    def _sell(self, symbol, price, score, date, data=None):
        """Execute sell order with dynamic cost optimization"""
        if symbol not in self.positions or self.positions[symbol]['quantity'] == 0:
            return
        
        position = self.positions[symbol]
        quantity = position['quantity']
        
        # Use dynamic slippage
        if data is not None:
            dynamic_slippage = self._calculate_dynamic_slippage(symbol, quantity, price, data)
            execution_price = price * (1 - dynamic_slippage)
        else:
            execution_price = price * (1 - self.base_slippage)
        
        # Calculate dynamic commission
        if data is not None:
            dynamic_commission = self._calculate_dynamic_commission(symbol, quantity, execution_price, data)
        else:
            dynamic_commission = self.base_commission
        
        # Execute sell
        proceeds = quantity * execution_price * (1 - dynamic_commission)
        
        # Calculate P&L
        cost = quantity * position['cost_basis']
        pnl = proceeds - cost
        pnl_pct = (execution_price / position['cost_basis'] - 1) * 100
        
        # Update cash and positions
        self.cash += proceeds
        self.positions[symbol] = {
            'quantity': 0,
            'cost_basis': 0,
            'entry_date': None,
            'entry_score': None
        }
        
        # Record trade
        trade = {
            'date': date,
            'symbol': symbol,
            'action': 'SELL',
            'quantity': quantity,
            'price': execution_price,
            'value': quantity * execution_price,
            'commission': quantity * execution_price * dynamic_commission,
            'commission_rate': dynamic_commission,
            'slippage_rate': dynamic_slippage if data is not None else self.base_slippage,
            'pnl': pnl,
            'pnl_pct': pnl_pct,
            'score': score,
            'cash_after': self.cash
        }
        self.trade_history.append(trade)
        
        print(f"  SELL {symbol}: {quantity} shares @ {execution_price:.2f} | P&L: {pnl:+,.2f} ({pnl_pct:+.2f}%) | Commission: {dynamic_commission*100:.3f}% | Cash: {self.cash:,.2f}")

    def _record_portfolio_state(self, data, date):
        """Record current portfolio state"""
        portfolio_value = self._calculate_portfolio_value(data, date)

        positions_snapshot = {}
        for symbol, pos in self.positions.items():
            if pos['quantity'] > 0:
                positions_snapshot[symbol] = {
                    'quantity': pos['quantity'],
                    'cost_basis': pos['cost_basis'],
                    'current_value': pos['quantity'] * self._get_current_price(symbol, data, date)
                }

        record = {
            'date': date,
            'total_value': portfolio_value,
            'cash': self.cash,
            'positions_value': portfolio_value - self.cash,
            'positions': positions_snapshot
        }
        self.portfolio_history.append(record)

    def _calculate_portfolio_value(self, data, date):
        """Calculate total portfolio value"""
        total = self.cash

        for symbol, position in self.positions.items():
            if position['quantity'] > 0 and symbol in data:
                current_price = self._get_current_price(symbol, data, date)
                total += position['quantity'] * current_price

        return total

    def _get_current_price(self, symbol, data, date):
        """Get current price for a symbol"""
        if symbol not in data:
            return 0

        df = data[symbol]
        if date in df.index:
            return df.loc[date, 'close']
        else:
            # Get most recent price
            return df['close'].iloc[-1]

    # ==================== New Methods (arXiv 2026 Papers) ====================

    def _calculate_dynamic_commission(self, symbol, quantity, price, data):
        """
        Calculate dynamic commission based on market conditions (arXiv:2606.21784)
        
        Adjusts commission based on:
        - Order size relative to daily volume (market impact)
        - Market volatility
        - Time of day (if intraday)
        
        Args:
            symbol: Stock symbol
            quantity: Order quantity (shares)
            price: Execution price
            data: Market data dict
            
        Returns:
            float: Adjusted commission rate
        """
        if not self.enable_dynamic_costs:
            return self.base_commission
        
        try:
            # Factor 1: Order size impact (square-root law)
            if symbol in data and data[symbol] is not None:
                df = data[symbol]
                avg_daily_volume = df['volume'].tail(20).mean()
                
                if avg_daily_volume > 0:
                    relative_size = quantity / avg_daily_volume
                    # Higher relative size = higher commission (to account for market impact)
                    size_multiplier = 1 + 0.5 * np.sqrt(relative_size)  # Square-root adjustment
                else:
                    size_multiplier = 1.0
            else:
                size_multiplier = 1.0
            
            # Factor 2: Market volatility
            if symbol in data and data[symbol] is not None:
                df = data[symbol]
                returns = df['close'].pct_change().tail(20)
                volatility = returns.std() * np.sqrt(252)  # Annualized
                
                # Higher volatility = higher commission (risk premium)
                vol_multiplier = 1 + 0.3 * min(volatility / 0.2, 2.0)  # Cap at 2x
            else:
                vol_multiplier = 1.0
            
            # Calculate adjusted commission
            adjusted_commission = self.base_commission * size_multiplier * vol_multiplier
            
            # Cap at 3x base commission
            adjusted_commission = min(adjusted_commission, self.base_commission * 3)
            
            return round(adjusted_commission, 6)
            
        except Exception as e:
            print(f"Error calculating dynamic commission for {symbol}: {e}")
            return self.base_commission

    def _calculate_dynamic_slippage(self, symbol, quantity, price, data):
        """
        Calculate dynamic slippage based on market liquidity (arXiv:2606.21784)
        
        Args:
            symbol: Stock symbol
            quantity: Order quantity (shares)
            price: Execution price
            data: Market data dict
            
        Returns:
            float: Adjusted slippage rate
        """
        if not self.enable_dynamic_costs:
            return self.base_slippage
        
        try:
            # Factor: Order size vs liquidity
            if symbol in data and data[symbol] is not None:
                df = data[symbol]
                avg_daily_volume = df['volume'].tail(20).mean()
                
                if avg_daily_volume > 0:
                    relative_size = quantity / avg_daily_volume
                    # Slippage increases with order size
                    slippage_adjustment = self.base_slippage * (1 + 2 * relative_size)
                else:
                    slippage_adjustment = self.base_slippage
            else:
                slippage_adjustment = self.base_slippage
            
            # Cap at 1% slippage
            slippage_adjustment = min(slippage_adjustment, 0.01)
            
            return round(slippage_adjustment, 6)
            
        except Exception as e:
            print(f"Error calculating dynamic slippage for {symbol}: {e}")
            return self.base_slippage

    def print_portfolio_summary(self):
        """Print current portfolio summary"""
        print(f"\n{'='*60}")
        print(f"Portfolio Summary")
        print(f"{'='*60}")
        print(f"Cash: {self.cash:,.2f}")
        print(f"Initial Capital: {self.initial_capital:,.2f}")

        if len(self.portfolio_history) > 0:
            latest = self.portfolio_history[-1]
            total_value = latest['total_value']
            total_return = (total_value / self.initial_capital - 1) * 100

            print(f"Total Portfolio Value: {total_value:,.2f}")
            print(f"Total Return: {total_return:+.2f}%")

            print(f"\nPositions:")
            if len(latest['positions']) > 0:
                for symbol, pos in latest['positions'].items():
                    current_value = pos['current_value']
                    cost = pos['quantity'] * pos['cost_basis']
                    pnl = current_value - cost
                    pnl_pct = (current_value / cost - 1) * 100 if cost > 0 else 0
                    print(f"  {symbol}: {pos['quantity']} shares | Cost: {pos['cost_basis']:.2f} | Value: {current_value:,.2f} | P&L: {pnl:+,.2f} ({pnl_pct:+.2f}%)")
            else:
                print(f"  No open positions")

        # Print trade history summary
        if len(self.trade_history) > 0:
            sell_trades = [t for t in self.trade_history if t['action'] in ['SELL']]
            if len(sell_trades) > 0:
                total_pnl = sum(t['pnl'] for t in sell_trades)
                winning_trades = [t for t in sell_trades if t['pnl'] > 0]
                win_rate = len(winning_trades) / len(sell_trades) * 100

                print(f"\nTrade History:")
                print(f"  Total Trades: {len(self.trade_history)}")
                print(f"  Completed Trades (Sells): {len(sell_trades)}")
                print(f"  Winning Trades: {len(winning_trades)}")
                print(f"  Win Rate: {win_rate:.2f}%")
                print(f"  Total Realized P&L: {total_pnl:+,.2f}")

    def save_state(self, filepath='trading_state.json'):
        """Save trading state to JSON file"""
        state = {
            'initial_capital': self.initial_capital,
            'cash': self.cash,
            'positions': self.positions,
            'portfolio_history': [
                {
                    'date': h['date'].strftime('%Y-%m-%d') if hasattr(h['date'], 'strftime') else h['date'],
                    'total_value': h['total_value'],
                    'cash': h['cash'],
                    'positions_value': h['positions_value']
                }
                for h in self.portfolio_history
            ],
            'trade_history': [
                {
                    'date': t['date'].strftime('%Y-%m-%d') if hasattr(t['date'], 'strftime') else t['date'],
                    'symbol': t['symbol'],
                    'action': t['action'],
                    'quantity': t['quantity'],
                    'price': t['price'],
                    'pnl': t.get('pnl', 0)
                }
                for t in self.trade_history
            ]
        }

        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)

        print(f"\nTrading state saved to: {filepath}")

    def load_state(self, filepath='trading_state.json'):
        """Load trading state from JSON file"""
        if not os.path.exists(filepath):
            print(f"No saved state found at {filepath}")
            return False

        with open(filepath, 'r') as f:
            state = json.load(f)

        self.initial_capital = state['initial_capital']
        self.cash = state['cash']
        self.positions = state['positions']

        print(f"Trading state loaded from: {filepath}")
        return True


if __name__ == "__main__":
    # Test the simulated broker
    from data_loader import MultiMarketDataLoader
    from scoring_engine import MultiFactorScorer
    from signal_generator import SignalGenerator

    print("Testing SimulatedBroker...")

    # Load data and generate signals
    loader = MultiMarketDataLoader()
    data = loader.load_data(
        {'ashare': ['600519.SH', '000858.SZ']},
        '2024-01-01', '2024-06-30'
    )

    scorer = MultiFactorScorer()
    fundamentals = loader.load_fundamental_data(list(data.keys()))
    macro = loader.load_macro_data()
    scores = scorer.calculate_scores(data, fundamentals, macro)

    generator = SignalGenerator()
    signals = generator.generate_signals(scores)

    # Run simulated trading
    broker = SimulatedBroker(initial_capital=100000)
    broker.execute_signals(signals, data)
    broker.print_portfolio_summary()
    broker.save_state()
