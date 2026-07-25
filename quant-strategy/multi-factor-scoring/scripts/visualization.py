"""
Visualization Module
Plotting and reporting for multi-factor scoring system
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import seaborn as sns

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")


class Visualizer:
    """Visualization tools for multi-factor scoring system"""

    def __init__(self, figsize=(14, 8)):
        self.figsize = figsize

    def plot_scores_heatmap(self, scores_df, title='Multi-Factor Scores Heatmap', save_path=None):
        """
        Plot heatmap of factor scores

        Args:
            scores_df: DataFrame with factor scores (columns: momentum, technical, volume, etc.)
            title: Plot title
            save_path: Path to save the plot
        """
        # Select only factor score columns
        factor_cols = ['momentum', 'technical', 'volume', 'fundamental', 'macro', 'sector', 'composite']
        plot_df = scores_df[[col for col in factor_cols if col in scores_df.columns]].T

        fig, ax = plt.subplots(figsize=self.figsize)

        # Create heatmap
        im = ax.imshow(plot_df.values, cmap='RdYlGn', aspect='auto', vmin=0, vmax=100)

        # Set ticks and labels
        ax.set_xticks(range(len(plot_df.columns)))
        ax.set_xticklabels(plot_df.columns, rotation=45, ha='right')
        ax.set_yticks(range(len(plot_df.index)))
        ax.set_yticklabels(plot_df.index)

        # Add colorbar
        plt.colorbar(im, ax=ax, label='Score (0-100)')

        # Add score values as text
        for i in range(len(plot_df.index)):
            for j in range(len(plot_df.columns)):
                text = ax.text(j, i, f"{plot_df.iloc[i, j]:.1f}",
                              ha="center", va="center", color="black", fontsize=8)

        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.set_xlabel('Stocks', fontsize=12)
        ax.set_ylabel('Factors', fontsize=12)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=100, bbox_inches='tight')
            print(f"Heatmap saved to: {save_path}")

        plt.show()

    def plot_portfolio_composition(self, positions, title='Portfolio Composition', save_path=None):
        """
        Plot portfolio composition pie chart

        Args:
            positions: Dict {symbol: {'quantity': int, 'current_value': float}}
            title: Plot title
            save_path: Path to save the plot
        """
        if not positions or sum(pos['current_value'] for pos in positions.values()) == 0:
            print("No positions to plot!")
            return

        symbols = []
        values = []

        for symbol, pos in positions.items():
            if pos['quantity'] > 0 and pos['current_value'] > 0:
                symbols.append(symbol)
                values.append(pos['current_value'])

        if len(symbols) == 0:
            print("No active positions to plot!")
            return

        fig, ax = plt.subplots(figsize=(10, 8))

        # Create pie chart
        colors = plt.cm.Set3(np.linspace(0, 1, len(symbols)))
        wedges, texts, autotexts = ax.pie(values, labels=symbols, autopct='%1.1f%%',
                                           colors=colors, startangle=90)

        # Style
        plt.setp(texts, size=10, weight="bold")
        plt.setp(autotexts, size=9, weight="bold", color="white")

        ax.set_title(title, fontsize=14, fontweight='bold')

        if save_path:
            plt.savefig(save_path, dpi=100, bbox_inches='tight')
            print(f"Portfolio composition saved to: {save_path}")

        plt.show()

    def plot_equity_curve(self, portfolio_history, benchmark_data=None, title='Portfolio Equity Curve', save_path=None):
        """
        Plot equity curve over time

        Args:
            portfolio_history: List of {date, total_value, cash, positions_value}
            benchmark_data: Dict {name: DataFrame with 'close' column} (optional)
            title: Plot title
            save_path: Path to save the plot
        """
        if not portfolio_history or len(portfolio_history) == 0:
            print("No portfolio history to plot!")
            return

        # Convert to DataFrame
        df = pd.DataFrame(portfolio_history)
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)

        fig, ax = plt.subplots(figsize=self.figsize)

        # Plot portfolio value
        ax.plot(df.index, df['total_value'], label='Portfolio Value', linewidth=2, color='blue')

        # Plot cash
        ax.plot(df.index, df['cash'], label='Cash', linewidth=1, color='green', linestyle='--')

        # Plot benchmark if provided
        if benchmark_data:
            for name, benchmark in benchmark_data.items():
                # Align dates
                benchmark_aligned = benchmark.reindex(df.index, method='ffill')
                if 'close' in benchmark_aligned.columns:
                    # Normalize to same starting point
                    normalized = benchmark_aligned['close'] / benchmark_aligned['close'].iloc[0] * df['total_value'].iloc[0]
                    ax.plot(df.index, normalized, label=f'Benchmark: {name}', linewidth=1, linestyle=':')

        # Formatting
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Value', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)

        # Format y-axis as currency
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.0f}'))

        # Format x-axis dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        plt.xticks(rotation=45)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=100, bbox_inches='tight')
            print(f"Equity curve saved to: {save_path}")

        plt.show()

    def plot_factor_exposure(self, scores_df, title='Factor Exposure Breakdown', save_path=None):
        """
        Plot factor exposure breakdown (average scores by factor)

        Args:
            scores_df: DataFrame with factor scores
            title: Plot title
            save_path: Path to save the plot
        """
        factor_cols = ['momentum', 'technical', 'volume', 'fundamental', 'macro', 'sector']
        available_factors = [col for col in factor_cols if col in scores_df.columns]

        if len(available_factors) == 0:
            print("No factor columns found!")
            return

        # Calculate average scores
        avg_scores = scores_df[available_factors].mean()

        fig, ax = plt.subplots(figsize=(10, 6))

        # Create bar chart
        colors = ['green' if score >= 50 else 'red' for score in avg_scores]
        bars = ax.bar(avg_scores.index, avg_scores.values, color=colors, alpha=0.7, edgecolor='black')

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                   f'{height:.1f}', ha='center', va='bottom', fontweight='bold')

        # Add horizontal line at 50 (neutral)
        ax.axhline(y=50, color='black', linestyle='--', linewidth=1, label='Neutral (50)')

        # Formatting
        ax.set_xlabel('Factors', fontsize=12)
        ax.set_ylabel('Average Score (0-100)', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_ylim(0, 100)
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')

        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=100, bbox_inches='tight')
            print(f"Factor exposure saved to: {save_path}")

        plt.show()

    def plot_top_bottom_stocks(self, scores_df, top_n=10, title='Top/Bottom Stocks by Composite Score', save_path=None):
        """
        Plot top and bottom N stocks by composite score

        Args:
            scores_df: DataFrame with composite scores
            top_n: Number of top/bottom stocks to show
            title: Plot title
            save_path: Path to save the plot
        """
        if 'composite' not in scores_df.columns:
            print("No composite score column found!")
            return

        # Sort by composite score
        sorted_df = scores_df.sort_values('composite', ascending=False)

        # Get top and bottom N
        top = sorted_df.head(top_n)
        bottom = sorted_df.tail(top_n)

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        # Plot top stocks
        colors_top = ['green' if score >= 70 else 'orange' for score in top['composite']]
        bars1 = ax1.barh(top.index, top['composite'], color=colors_top, alpha=0.7)
        ax1.set_xlabel('Composite Score', fontsize=10)
        ax1.set_title(f'Top {top_n} Stocks', fontsize=12, fontweight='bold')
        ax1.set_xlim(0, 100)
        ax1.grid(True, alpha=0.3, axis='x')

        # Add value labels
        for bar in bars1:
            width = bar.get_width()
            ax1.text(width + 1, bar.get_y() + bar.get_height()/2,
                    f'{width:.1f}', ha='left', va='center', fontsize=8)

        # Plot bottom stocks
        colors_bottom = ['red' if score <= 30 else 'orange' for score in bottom['composite']]
        bars2 = ax2.barh(bottom.index, bottom['composite'], color=colors_bottom, alpha=0.7)
        ax2.set_xlabel('Composite Score', fontsize=10)
        ax2.set_title(f'Bottom {top_n} Stocks', fontsize=12, fontweight='bold')
        ax2.set_xlim(0, 100)
        ax2.grid(True, alpha=0.3, axis='x')

        # Add value labels
        for bar in bars2:
            width = bar.get_width()
            ax2.text(width + 1, bar.get_y() + bar.get_height()/2,
                    f'{width:.1f}', ha='left', va='center', fontsize=8)

        fig.suptitle(title, fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.subplots_adjust(top=0.85)

        if save_path:
            plt.savefig(save_path, dpi=100, bbox_inches='tight')
            print(f"Top/bottom stocks saved to: {save_path}")

        plt.show()

    def generate_html_report(self, scores_df, signals_df, portfolio_state, output_path='report.html'):
        """
        Generate HTML report with scores, signals, and portfolio state

        Args:
            scores_df: DataFrame with factor scores
            signals_df: DataFrame with trading signals
            portfolio_state: Dict with portfolio state
            output_path: Path to save HTML report
        """
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Multi-Factor Scoring Report</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        h1 {{
            color: #333;
            text-align: center;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background-color: white;
            margin-bottom: 20px;
        }}
        th, td {{
            padding: 10px;
            text-align: left;
            border: 1px solid #ddd;
        }}
        th {{
            background-color: #4CAF50;
            color: white;
        }}
        .buy {{
            background-color: #d4edda;
            color: #155724;
        }}
        .sell {{
            background-color: #f8d7da;
            color: #721c24;
        }}
        .hold {{
            background-color: #fff3cd;
            color: #856404;
        }}
        .section {{
            background-color: white;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
    </style>
</head>
<body>
    <h1>Multi-Factor Scoring Quantitative Trading Report</h1>
    <p style="text-align: center;">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

    <div class="section">
        <h2>Trading Signals</h2>
        {signals_df.to_html(classes='table', index=False) if signals_df is not None else 'No signals generated'}
    </div>

    <div class="section">
        <h2>Factor Scores</h2>
        {scores_df.to_html(classes='table') if scores_df is not None else 'No scores calculated'}
    </div>

    <div class="section">
        <h2>Portfolio State</h2>
        <p><strong>Total Value:</strong> {portfolio_state.get('total_value', 0):,.2f}</p>
        <p><strong>Cash:</strong> {portfolio_state.get('cash', 0):,.2f}</p>
        <p><strong>Positions Value:</strong> {portfolio_state.get('positions_value', 0):,.2f}</p>
    </div>
</body>
</html>
"""

        with open(output_path, 'w') as f:
            f.write(html_content)

        print(f"HTML report saved to: {output_path}")


if __name__ == "__main__":
    # Test the visualizer
    print("Testing Visualizer...")

    # Create sample data
    scores_df = pd.DataFrame({
        'momentum': [80, 60, 40, 70, 50],
        'technical': [70, 65, 45, 60, 55],
        'volume': [60, 55, 50, 65, 40],
        'fundamental': [75, 70, 60, 55, 65],
        'macro': [50, 50, 50, 50, 50],
        'sector': [65, 60, 55, 70, 50],
        'composite': [70, 62, 50, 65, 52]
    }, index=['600519.SH', '000858.SZ', '601318.SH', '000333.SZ', '600036.SH'])

    # Plot heatmap
    viz = Visualizer()
    viz.plot_scores_heatmap(scores_df, title='Test Heatmap')

    print("Visualizer test complete!")
