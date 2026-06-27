"""
投资组合优化脚本
基于现代投资组合理论（MPT）计算有效前沿和优化组合
"""

import sys
import json
import argparse
import pandas as pd
import numpy as np
import scipy.optimize as sco
from typing import List, Dict, Optional


def fetch_stock_data(
    stocks: List[str],
    start_date: str,
    end_date: str,
    use_westock: bool = True,
    data_file: Optional[str] = None
) -> pd.DataFrame:
    """
    获取股票数据
    
    Args:
        stocks: 股票代码列表
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)
        use_westock: 是否使用 westock-data（需要 MCP 环境）
        data_file: 数据文件路径（从 CSV 读取）
    
    Returns:
        价格数据 DataFrame（索引为日期，列为股票代码）
    """
    # 优先从 CSV 文件读取
    if data_file:
        print(f"从文件读取数据：{data_file}")
        return pd.read_csv(data_file, index_col=0, parse_dates=True)
    
    if use_westock:
        # 尝试使用 westock-data（需要在 WorkBuddy 环境中运行）
        try:
            # 这里需要调用 westock-data skill
            # 由于是脚本，我们假设数据已经准备好，从 CSV 读取
            print("提示：使用 westock-data 获取数据需要在 WorkBuddy 中调用")
            print("当前从 CSV 文件读取示例数据...")
            return pd.read_csv('data/sample_prices.csv', index_col=0, parse_dates=True)
        except Exception as e:
            print(f"westock-data 调用失败：{e}")
            print("降级到 akshare...")
    
    # 使用 akshare 作为备选方案
    try:
        import akshare as ak
        
        data = {}
        for stock in stocks:
            # 转换股票代码格式
            symbol = stock.replace('.SH', '').replace('.SZ', '')
            df = ak.stock_zh_a_hist(
                symbol=symbol,
                start_date=start_date.replace('-', ''),
                end_date=end_date.replace('-', ''),
                adjust="qfq"
            )
            data[stock] = df.set_index('日期')['收盘']
        
        price_data = pd.DataFrame(data)
        return price_data
    
    except ImportError:
        raise ImportError("需要安装 akshare：pip install akshare")


def preprocess_data(price_data: pd.DataFrame) -> tuple:
    """
    预处理价格数据
    
    Returns:
        (returns, annual_returns, cov_matrix)
    """
    # 1. 删除交易天数不足的股票
    min_trading_days = 252
    valid_stocks = price_data.columns[price_data.notna().sum() >= min_trading_days]
    price_data = price_data[valid_stocks]
    
    # 2. 填充缺失值
    price_data = price_data.fillna(method='ffill')
    
    # 3. 计算对数收益率
    returns = np.log(price_data / price_data.shift(1)).dropna()
    
    # 4. 转换为年化收益率
    annual_returns = returns.mean() * 252
    
    # 5. 计算年化协方差矩阵
    cov_matrix = returns.cov() * 252
    
    return returns, annual_returns, cov_matrix


def minimize_risk(
    target_return: float,
    annual_returns: pd.Series,
    cov_matrix: pd.DataFrame,
    allow_short: bool = False
) -> Dict:
    """最小化风险（给定目标收益率）"""
    n_assets = len(annual_returns)
    
    def portfolio_variance(weights):
        return np.dot(weights.T, np.dot(cov_matrix, weights))
    
    constraints = [
        {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
        {'type': 'eq', 'fun': lambda x: np.dot(x, annual_returns) - target_return}
    ]
    
    bounds = tuple((-1, 1) for _ in range(n_assets)) if allow_short else tuple((0, 1) for _ in range(n_assets))
    initial_guess = np.array([1.0 / n_assets] * n_assets)
    
    result = sco.minimize(portfolio_variance, initial_guess, method='SLSQP', bounds=bounds, constraints=constraints)
    
    if not result.success:
        raise ValueError("优化失败")
    
    optimal_weights = result.x
    portfolio_return = np.dot(optimal_weights, annual_returns)
    portfolio_risk = np.sqrt(result.fun)
    sharpe_ratio = portfolio_return / portfolio_risk
    
    return {
        'weights': optimal_weights.tolist(),
        'return': float(portfolio_return),
        'risk': float(portfolio_risk),
        'sharpe_ratio': float(sharpe_ratio)
    }


def maximize_sharpe(
    annual_returns: pd.Series,
    cov_matrix: pd.DataFrame,
    risk_free_rate: float = 0.025,
    allow_short: bool = False
) -> Dict:
    """最大化夏普比率"""
    n_assets = len(annual_returns)
    
    def negative_sharpe(weights):
        portfolio_return = np.dot(weights, annual_returns)
        portfolio_risk = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        return -(portfolio_return - risk_free_rate) / portfolio_risk
    
    constraints = {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}
    bounds = tuple((-1, 1) for _ in range(n_assets)) if allow_short else tuple((0, 1) for _ in range(n_assets))
    initial_guess = np.array([1.0 / n_assets] * n_assets)
    
    result = sco.minimize(negative_sharpe, initial_guess, method='SLSQP', bounds=bounds, constraints=constraints)
    
    if not result.success:
        raise ValueError("优化失败")
    
    optimal_weights = result.x
    portfolio_return = np.dot(optimal_weights, annual_returns)
    portfolio_risk = np.sqrt(np.dot(optimal_weights.T, np.dot(cov_matrix, optimal_weights)))
    sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_risk
    
    return {
        'weights': optimal_weights.tolist(),
        'return': float(portfolio_return),
        'risk': float(portfolio_risk),
        'sharpe_ratio': float(sharpe_ratio)
    }


def main():
    parser = argparse.ArgumentParser(description='投资组合优化')
    parser.add_argument('--stocks', nargs='+', help='股票代码列表')
    parser.add_argument('--start-date', help='开始日期 (YYYY-MM-DD)')
    parser.add_argument('--end-date', help='结束日期 (YYYY-MM-DD)')
    parser.add_argument('--risk-free-rate', type=float, default=0.025, help='无风险利率')
    parser.add_argument('--allow-short', action='store_true', help='允许做空')
    parser.add_argument('--data-file', help='数据文件路径（CSV）')
    parser.add_argument('--output', help='输出 JSON 文件路径')
    
    args = parser.parse_args()
    
    # 1. 获取数据
    print("正在获取数据...")
    if args.data_file:
        price_data = fetch_stock_data(args.stocks or [], args.start_date or '', args.end_date or '', data_file=args.data_file)
    else:
        price_data = fetch_stock_data(args.stocks or ['600519.SH', '000858.SZ', '603288.SH', '600887.SH'], 
                                        args.start_date or '2023-01-01', 
                                        args.end_date or '2023-12-31')
    
    # 2. 预处理
    print("正在预处理数据...")
    returns, annual_returns, cov_matrix = preprocess_data(price_data)
    
    # 3. 优化
    print("正在优化投资组合...")
    result = maximize_sharpe(annual_returns, cov_matrix, args.risk_free_rate, args.allow_short)
    
    # 4. 输出结果
    print("\n优化结果：")
    print(f"  预期收益率：{result['return']:.2%}")
    print(f"  风险（波动率）：{result['risk']:.2%}")
    print(f"  夏普比率：{result['sharpe_ratio']:.2f}")
    print(f"\n权重分配：")
    for stock, weight in zip(annual_returns.index, result['weights']):
        print(f"  {stock}: {weight:.2%}")
    
    # 5. 保存结果
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\n结果已保存到：{args.output}")
    
    # 6. 验证验收标准
    if result['sharpe_ratio'] > 1:
        print(f"\n✅ 验收标准达成：夏普比率 {result['sharpe_ratio']:.2f} > 1")
    else:
        print(f"\n❌ 验收标准未达成：夏普比率 {result['sharpe_ratio']:.2f} <= 1")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
