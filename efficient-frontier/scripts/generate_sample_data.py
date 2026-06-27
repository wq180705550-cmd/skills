"""
生成示例股票数据用于测试
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os


def generate_sample_data(output_file: str = 'data/sample_prices.csv'):
    """
    生成示例价格数据（模拟 A股消费板块）
    
    Args:
        output_file: 输出文件路径
    """
    # 1. 定义日期范围
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 12, 31)
    dates = pd.date_range(start_date, end_date, freq='B')  # 仅工作日
    
    # 2. 定义股票和初始价格
    stocks = {
        '600519.SH': 1800,  # 贵州茅台
        '000858.SZ': 150,    # 五粮液
        '603288.SH': 80,     # 海天味业
        '600887.SH': 30      # 伊利股份
    }
    
    # 3. 生成模拟价格数据（几何布朗运动）
    np.random.seed(42)
    price_data = pd.DataFrame(index=dates)
    
    for stock, initial_price in stocks.items():
        # 模拟日度收益率（正态分布）
        # 均值 0.0005 (年化约 12.6%)，波动率 0.02 (年化约 31.8%)
        returns = np.random.normal(0.0005, 0.02, len(dates))
        
        # 计算价格
        prices = [initial_price]
        for ret in returns[1:]:
            prices.append(prices[-1] * (1 + ret))
        
        price_data[stock] = prices
    
    # 4. 创建输出目录
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # 5. 保存数据
    price_data.to_csv(output_file)
    print(f"示例数据已生成：{output_file}")
    print(f"  股票池：{list(stocks.keys())}")
    print(f"  日期范围：{start_date.date()} 至 {end_date.date()}")
    print(f"  数据点数：{len(dates)}")
    
    # 6. 显示统计信息
    print(f"\n统计信息：")
    returns = price_data.pct_change().dropna()
    annual_returns = returns.mean() * 252
    for stock in price_data.columns:
        print(f"  {stock}:")
        print(f"    年化收益率：{annual_returns[stock]:.2%}")
        print(f"    年化波动率：{returns[stock].std() * np.sqrt(252):.2%}")


if __name__ == '__main__':
    generate_sample_data()
