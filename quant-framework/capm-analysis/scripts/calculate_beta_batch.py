"""
批量计算股票池的 Beta 系数

用于为量化框架提供 Beta 因子数据。
"""

import sys
import json
import argparse
import pandas as pd
from typing import Dict, List

# 导入 CAPM 核心计算模块
sys.path.insert(0, '.')
from capm_core import (
    get_risk_free_rate,
    get_market_data,
    get_stock_data,
    calculate_returns,
    calculate_beta
)


def calculate_beta_batch(
    stocks: List[str],
    benchmark: str = '000300.SH',
    start_date: str = '2023-01-01',
    end_date: str = '2023-12-31',
    risk_free_tenor: str = '10Y',
    frequency: str = 'daily'
) -> Dict:
    """
    批量计算股票池的 Beta 系数
    
    Args:
        stocks: 股票代码列表
        benchmark: 市场基准代码
        start_date: 开始日期
        end_date: 结束日期
        risk_free_tenor: 无风险利率期限
        frequency: 数据频率
    
    Returns:
        包含 Beta 系数矩阵的字典
    """
    print(f"\n{'='*60}")
    print("批量计算 Beta 系数")
    print(f"{'='*60}")
    print(f"股票池：{len(stocks)} 只")
    print(f"市场基准：{benchmark}")
    print(f"时间段：{start_date} 至 {end_date}")
    print(f"{'='*60}\n")
    
    # 1. 获取无风险利率
    print("【步骤 1/4】获取无风险利率...")
    if benchmark.endswith('.SH') or benchmark.endswith('.SZ'):
        market = 'CN'
    else:
        market = 'US'
    
    risk_free_rate = get_risk_free_rate(market, risk_free_tenor)
    print(f"  无风险利率（{risk_free_tenor}）：{risk_free_rate:.2%}\n")
    
    # 2. 获取市场基准数据
    print("【步骤 2/4】获取市场基准数据...")
    market_prices = get_market_data(benchmark, start_date, end_date, frequency)
    market_returns = calculate_returns(market_prices)
    print(f"  市场基准数据：{len(market_returns)} 条记录\n")
    
    # 3. 批量计算 Beta
    print("【步骤 3/4】批量计算 Beta 系数...")
    beta_results = {}
    failed_stocks = []
    
    for i, stock in enumerate(stocks):
        try:
            # 获取股票数据
            stock_prices = get_stock_data(stock, start_date, end_date, frequency)
            stock_returns = calculate_returns(stock_prices)
            
            # 计算 Beta
            beta_result = calculate_beta(
                stock_returns.iloc[:, 0],
                market_returns.iloc[:, 0],
                risk_free_rate
            )
            
            beta_results[stock] = {
                'beta': beta_result['beta'],
                'alpha': beta_result['alpha'],
                'r_squared': beta_result['r_squared'],
                'p_value': beta_result['p_value']
            }
            
            # 打印进度
            if (i + 1) % 10 == 0 or i == len(stocks) - 1:
                print(f"  进度：{i+1}/{len(stocks)} ({((i+1)/len(stocks)*100):.1f}%)")
        
        except Exception as e:
            failed_stocks.append(stock)
            print(f"  警告：计算 {stock} 失败：{e}")
    
    print(f"\n  成功：{len(beta_results)}/{len(stocks)}")
    if failed_stocks:
        print(f"  失败：{len(failed_stocks)} 只（{', '.join(failed_stocks)}）")
    print()
    
    # 4. 汇总结果
    print("【步骤 4/4】汇总结果...")
    
    # 转换为 DataFrame
    beta_df = pd.DataFrame(beta_results).T
    beta_df.index.name = 'stock'
    beta_df.reset_index(inplace=True)
    
    # 统计摘要
    print(f"\nBeta 系数统计摘要：")
    print(f"  平均值：{beta_df['beta'].mean():.4f}")
    print(f"  中位数：{beta_df['beta'].median():.4f}")
    print(f"  标准差：{beta_df['beta'].std():.4f}")
    print(f"  最小值：{beta_df['beta'].min():.4f}")
    print(f"  最大值：{beta_df['beta'].max():.4f}")
    print(f"  Beta > 1 的数量：{(beta_df['beta'] > 1).sum()}")
    print(f"  Beta < 1 的数量：{(beta_df['beta'] < 1).sum()}")
    
    result = {
        'benchmark': benchmark,
        'start_date': start_date,
        'end_date': end_date,
        'risk_free_rate': risk_free_rate,
        'risk_free_tenor': risk_free_tenor,
        'n_stocks': len(beta_results),
        'n_failed': len(failed_stocks),
        'failed_stocks': failed_stocks,
        'beta_results': beta_results
    }
    
    print(f"\n{'='*60}")
    print("批量计算完成！")
    print(f"{'='*60}\n")
    
    return result


def main():
    parser = argparse.ArgumentParser(description='批量计算 Beta 系数')
    parser.add_argument('--stocks', nargs='+', help='股票代码列表')
    parser.add_argument('--stocks-file', help='包含股票代码的文件（每行一只）')
    parser.add_argument('--benchmark', default='000300.SH', help='市场基准代码')
    parser.add_argument('--start-date', default='2023-01-01', help='开始日期（YYYY-MM-DD）')
    parser.add_argument('--end-date', default='2023-12-31', help='结束日期（YYYY-MM-DD）')
    parser.add_argument('--risk-free-tenor', default='10Y', help='无风险利率期限')
    parser.add_argument('--frequency', default='daily', help='数据频率')
    parser.add_argument('--output', help='输出 JSON 文件路径')
    parser.add_argument('--output-csv', help='输出 CSV 文件路径')
    
    args = parser.parse_args()
    
    # 获取股票列表
    stocks = []
    if args.stocks:
        stocks = args.stocks
    elif args.stocks_file:
        with open(args.stocks_file, 'r', encoding='utf-8') as f:
            stocks = [line.strip() for line in f if line.strip()]
    else:
        print("错误：必须提供 --stocks 或 --stocks-file")
        sys.exit(1)
    
    # 批量计算 Beta
    result = calculate_beta_batch(
        stocks=stocks,
        benchmark=args.benchmark,
        start_date=args.start_date,
        end_date=args.end_date,
        risk_free_tenor=args.risk_free_tenor,
        frequency=args.frequency
    )
    
    # 保存结果
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"结果已保存到：{args.output}")
    
    if args.output_csv:
        # 转换为 CSV
        beta_df = pd.DataFrame(result['beta_results']).T
        beta_df.index.name = 'stock'
        beta_df.to_csv(args.output_csv, encoding='utf-8-sig')
        print(f"CSV 已保存到：{args.output_csv}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
