"""
回测框架脚本（简化版）
用于验证投资组合的历史表现
"""

import sys
import json
import argparse
import pandas as pd
import numpy as np
from typing import Dict, List


def backtest_portfolio(
    weights: List[float],
    price_data: pd.DataFrame,
    initial_capital: float = 1000000
) -> Dict:
    """
    回测投资组合
    
    Args:
        weights: 投资组合权重
        price_data: 价格数据
        initial_capital: 初始资金
    
    Returns:
        回测结果字典
    """
    # 1. 计算每日收益率
    returns = price_data.pct_change().dropna()
    
    # 2. 计算投资组合每日收益率
    portfolio_returns = (returns * weights).sum(axis=1)
    
    # 3. 计算累积净值
    cumulative_returns = (1 + portfolio_returns).cumprod()
    net_value = initial_capital * cumulative_returns
    
    # 4. 计算回测指标
    total_return = cumulative_returns.iloc[-1] - 1
    annual_return = (1 + total_return) ** (252 / len(portfolio_returns)) - 1
    annual_volatility = portfolio_returns.std() * np.sqrt(252)
    sharpe_ratio = annual_return / annual_volatility if annual_volatility > 0 else 0
    
    # 5. 计算最大回撤
    peak = net_value.expanding().max()
    drawdown = (net_value - peak) / peak
    max_drawdown = drawdown.min()
    
    return {
        'total_return': float(total_return),
        'annual_return': float(annual_return),
        'annual_volatility': float(annual_volatility),
        'sharpe_ratio': float(sharpe_ratio),
        'max_drawdown': float(max_drawdown),
        'final_net_value': float(net_value.iloc[-1])
    }


def plot_backtest_results(net_value: pd.Series, title: str = '投资组合回测结果'):
    """绘制回测结果"""
    try:
        import matplotlib.pyplot as plt
        
        fig, axes = plt.subplots(2, 1, figsize=(12, 8))
        
        # 1. 净值曲线
        axes[0].plot(net_value.index, net_value.values, 'b-', linewidth=2)
        axes[0].set_title('净值曲线')
        axes[0].set_ylabel('净值')
        axes[0].grid(True, alpha=0.3)
        
        # 2. 回撤曲线
        peak = net_value.expanding().max()
        drawdown = (net_value - peak) / peak
        axes[1].fill_between(drawdown.index, 0, drawdown.values, color='red', alpha=0.3)
        axes[1].plot(drawdown.index, drawdown.values, 'r-', linewidth=1)
        axes[1].set_title('回撤曲线')
        axes[1].set_ylabel('回撤')
        axes[1].set_xlabel('日期')
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('backtest_result.png', dpi=300, bbox_inches='tight')
        print(f"\n回测结果图已保存：backtest_result.png")
        
    except ImportError:
        print("提示：安装 matplotlib 以生成图表：pip install matplotlib")


def main():
    parser = argparse.ArgumentParser(description='回测投资组合')
    parser.add_argument('--weights', nargs='+', type=float, help='投资组合权重')
    parser.add_argument('--price-data', help='价格数据 CSV 文件')
    parser.add_argument('--initial-capital', type=float, default=1000000, help='初始资金')
    parser.add_argument('--plot', action='store_true', help='生成回测图表')
    
    args = parser.parse_args()
    
    # 1. 加载价格数据
    price_data = pd.read_csv(args.price_data, index_col=0, parse_dates=True)
    
    # 2. 回测
    result = backtest_portfolio(args.weights, price_data, args.initial_capital)
    
    # 3. 输出结果
    print("回测结果：")
    print(f"  总收益率：{result['total_return']:.2%}")
    print(f"  年化收益率：{result['annual_return']:.2%}")
    print(f"  年化波动率：{result['annual_volatility']:.2%}")
    print(f"  夏普比率：{result['sharpe_ratio']:.2f}")
    print(f"  最大回撤：{result['max_drawdown']:.2%}")
    print(f"  最终净值：{result['final_net_value']:.2f}")
    
    # 4. 生成图表
    if args.plot:
        # 重新计算净值用于绘图
        returns = price_data.pct_change().dropna()
        portfolio_returns = (returns * args.weights).sum(axis=1)
        cumulative_returns = (1 + portfolio_returns).cumprod()
        net_value = args.initial_capital * cumulative_returns
        plot_backtest_results(net_value)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
