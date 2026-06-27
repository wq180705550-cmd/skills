"""
投资组合优化模块

整合 efficient-frontier 功能，提供投资组合优化能力。
"""

import sys
import json
import argparse
import pandas as pd
import numpy as np
import scipy.optimize as sco
from typing import List, Dict, Optional, Tuple


class PortfolioOptimizer:
    """
    投资组合优化器
    
    支持三种优化目标：
    1. 最小化风险（给定目标收益率）
    2. 最大化夏普比率
    3. 最大化预期收益率（给定风险约束）
    """
    
    def __init__(
        self,
        expected_returns: pd.Series,
        cov_matrix: pd.DataFrame,
        risk_free_rate: float = 0.025
    ):
        """
        初始化投资组合优化器
        
        Args:
            expected_returns: 预期收益率序列（索引为股票代码）
            cov_matrix: 协方差矩阵
            risk_free_rate: 无风险利率
        """
        self.expected_returns = expected_returns
        self.cov_matrix = cov_matrix
        self.risk_free_rate = risk_free_rate
        self.n_assets = len(expected_returns)
    
    def minimize_risk(
        self,
        target_return: float,
        allow_short: bool = False
    ) -> Dict:
        """
        最小化风险（给定目标收益率）
        
        Args:
            target_return: 目标收益率
            allow_short: 是否允许做空
        
        Returns:
            优化结果字典
        """
        def portfolio_variance(weights):
            return np.dot(weights.T, np.dot(self.cov_matrix, weights))
        
        constraints = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
            {'type': 'eq', 'fun': lambda x: np.dot(x, self.expected_returns) - target_return}
        ]
        
        bounds = tuple((-1, 1) for _ in range(self.n_assets)) if allow_short else tuple((0, 1) for _ in range(self.n_assets))
        initial_guess = np.array([1.0 / self.n_assets] * self.n_assets)
        
        result = sco.minimize(portfolio_variance, initial_guess, method='SLSQP', bounds=bounds, constraints=constraints)
        
        if not result.success:
            raise ValueError("优化失败")
        
        optimal_weights = result.x
        portfolio_return = np.dot(optimal_weights, self.expected_returns)
        portfolio_risk = np.sqrt(result.fun)
        sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_risk
        
        return {
            'weights': optimal_weights.tolist(),
            'return': float(portfolio_return),
            'risk': float(portfolio_risk),
            'sharpe_ratio': float(sharpe_ratio)
        }
    
    def maximize_sharpe(
        self,
        allow_short: bool = False
    ) -> Dict:
        """
        最大化夏普比率
        
        Args:
            allow_short: 是否允许做空
        
        Returns:
            优化结果字典
        """
        def negative_sharpe(weights):
            portfolio_return = np.dot(weights, self.expected_returns)
            portfolio_risk = np.sqrt(np.dot(weights.T, np.dot(self.cov_matrix, weights)))
            return -(portfolio_return - self.risk_free_rate) / portfolio_risk
        
        constraints = {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}
        bounds = tuple((-1, 1) for _ in range(self.n_assets)) if allow_short else tuple((0, 1) for _ in range(self.n_assets))
        initial_guess = np.array([1.0 / self.n_assets] * self.n_assets)
        
        result = sco.minimize(negative_sharpe, initial_guess, method='SLSQP', bounds=bounds, constraints=constraints)
        
        if not result.success:
            raise ValueError("优化失败")
        
        optimal_weights = result.x
        portfolio_return = np.dot(optimal_weights, self.expected_returns)
        portfolio_risk = np.sqrt(np.dot(optimal_weights.T, np.dot(self.cov_matrix, optimal_weights)))
        sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_risk
        
        return {
            'weights': optimal_weights.tolist(),
            'return': float(portfolio_return),
            'risk': float(portfolio_risk),
            'sharpe_ratio': float(sharpe_ratio)
        }
    
    def maximize_return(
        self,
        target_risk: float,
        allow_short: bool = False
    ) -> Dict:
        """
        最大化预期收益率（给定风险约束）
        
        Args:
            target_risk: 目标风险（波动率）
            allow_short: 是否允许做空
        
        Returns:
            优化结果字典
        """
        def negative_return(weights):
            return -np.dot(weights, self.expected_returns)
        
        constraints = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
            {'type': 'eq', 'fun': lambda x: np.sqrt(np.dot(x.T, np.dot(self.cov_matrix, x))) - target_risk}
        ]
        
        bounds = tuple((-1, 1) for _ in range(self.n_assets)) if allow_short else tuple((0, 1) for _ in range(self.n_assets))
        initial_guess = np.array([1.0 / self.n_assets] * self.n_assets)
        
        result = sco.minimize(negative_return, initial_guess, method='SLSQP', bounds=bounds, constraints=constraints)
        
        if not result.success:
            raise ValueError("优化失败")
        
        optimal_weights = result.x
        portfolio_return = np.dot(optimal_weights, self.expected_returns)
        portfolio_risk = np.sqrt(np.dot(optimal_weights.T, np.dot(self.cov_matrix, optimal_weights)))
        sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_risk
        
        return {
            'weights': optimal_weights.tolist(),
            'return': float(portfolio_return),
            'risk': float(portfolio_risk),
            'sharpe_ratio': float(sharpe_ratio)
        }
    
    def calculate_efficient_frontier(
        self,
        n_points: int = 100,
        allow_short: bool = False
    ) -> pd.DataFrame:
        """
        计算有效前沿
        
        Args:
            n_points: 有效前沿上的点数
            allow_short: 是否允许做空
        
        Returns:
            有效前沿 DataFrame（包含 return、risk、sharpe_ratio 列）
        """
        # 计算最小风险组合和最大夏普比率组合
        min_risk_result = self.minimize_risk(
            target_return=self.expected_returns.min(),
            allow_short=allow_short
        )
        max_sharpe_result = self.maximize_sharpe(allow_short=allow_short)
        
        # 在最小风险和最大夏普比率之间生成点
        min_risk = min_risk_result['risk']
        max_risk = max_sharpe_result['risk']
        
        target_risks = np.linspace(min_risk, max_risk * 1.5, n_points)
        
        efficient_frontier = []
        for target_risk in target_risks:
            try:
                result = self.maximize_return(target_risk, allow_short)
                efficient_frontier.append(result)
            except:
                continue
        
        return pd.DataFrame(efficient_frontier)


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description='投资组合优化')
    parser.add_argument('--expected-returns', help='预期收益率 JSON 文件')
    parser.add_argument('--cov-matrix', help='协方差矩阵 CSV 文件')
    parser.add_argument('--risk-free-rate', type=float, default=0.025, help='无风险利率')
    parser.add_argument('--method', choices=['min_risk', 'max_sharpe', 'max_return'], default='max_sharpe', help='优化方法')
    parser.add_argument('--target-return', type=float, help='目标收益率（min_risk 方法）')
    parser.add_argument('--target-risk', type=float, help='目标风险（max_return 方法）')
    parser.add_argument('--allow-short', action='store_true', help='允许做空')
    parser.add_argument('--output', help='输出 JSON 文件路径')
    
    args = parser.parse_args()
    
    # 加载数据
    expected_returns = pd.Series(json.load(open(args.expected_returns)))
    cov_matrix = pd.read_csv(args.cov_matrix, index_col=0)
    
    # 创建优化器
    optimizer = PortfolioOptimizer(
        expected_returns=expected_returns,
        cov_matrix=cov_matrix,
        risk_free_rate=args.risk_free_rate
    )
    
    # 执行优化
    if args.method == 'min_risk':
        result = optimizer.minimize_risk(args.target_return, args.allow_short)
    elif args.method == 'max_sharpe':
        result = optimizer.maximize_sharpe(args.allow_short)
    elif args.method == 'max_return':
        result = optimizer.maximize_return(args.target_risk, args.allow_short)
    
    # 输出结果
    print("\n" + "="*80)
    print("投资组合优化结果：")
    print("="*80)
    print(f"预期收益率：{result['return']:.2%}")
    print(f"风险（波动率）：{result['risk']:.2%}")
    print(f"夏普比率：{result['sharpe_ratio']:.2f}")
    print(f"\n权重分配：")
    for stock, weight in zip(expected_returns.index, result['weights']):
        print(f"  {stock}: {weight:.2%}")
    
    # 保存结果
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\n结果已保存到：{args.output}")


if __name__ == '__main__':
    main()
