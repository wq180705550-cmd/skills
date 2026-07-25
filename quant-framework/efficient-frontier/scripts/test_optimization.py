"""
测试脚本：验证优化功能
"""

import sys
import os
sys.path.insert(0, '.')

from optimize import fetch_stock_data, preprocess_data, maximize_sharpe
from generate_sample_data import generate_sample_data


def test_optimization():
    """测试投资组合优化"""
    print("="*50)
    print("开始测试 efficient-frontier skill")
    print("="*50)
    
    # 1. 生成示例数据
    print("\n[步骤 1/4] 生成示例数据...")
    generate_sample_data('data/sample_prices.csv')
    
    # 2. 加载数据
    print("\n[步骤 2/4] 加载数据...")
    price_data = fetch_stock_data(
        ['600519.SH', '000858.SZ', '603288.SH', '600887.SH'],
        '2023-01-01',
        '2023-12-31',
        data_file='data/sample_prices.csv'
    )
    print(f"  数据形状：{price_data.shape}")
    print(f"  股票池：{list(price_data.columns)}")
    
    # 3. 预处理
    print("\n[步骤 3/4] 预处理数据...")
    returns, annual_returns, cov_matrix = preprocess_data(price_data)
    
    print(f"\n  年化收益率：")
    for stock, ret in annual_returns.items():
        print(f"    {stock}: {ret:.2%}")
    
    print(f"\n  年化波动率：")
    volatilities = np.sqrt(np.diag(cov_matrix))
    for stock, vol in zip(annual_returns.index, volatilities):
        print(f"    {stock}: {vol:.2%}")
    
    # 4. 优化
    print("\n[步骤 4/4] 优化投资组合...")
    result = maximize_sharpe(annual_returns, cov_matrix, risk_free_rate=0.025, allow_short=False)
    
    # 5. 验证验收标准
    print("\n" + "="*50)
    print("优化结果：")
    print(f"  预期收益率：{result['return']:.2%}")
    print(f"  风险（波动率）：{result['risk']:.2%}")
    print(f"  夏普比率：{result['sharpe_ratio']:.2f}")
    
    print(f"\n权重分配：")
    for stock, weight in zip(annual_returns.index, result['weights']):
        print(f"  {stock}: {weight:.2%}")
    
    # 6. 验收标准检查
    print("\n" + "="*50)
    if result['sharpe_ratio'] > 1:
        print(f"✅ 验收标准达成：夏普比率 {result['sharpe_ratio']:.2f} > 1")
        print("\n测试通过！")
        return True
    else:
        print(f"❌ 验收标准未达成：夏普比率 {result['sharpe_ratio']:.2f} <= 1")
        print("\n测试失败！")
        return False


if __name__ == '__main__':
    # 导入 numpy（在函数内部使用）
    import numpy as np
    
    success = test_optimization()
    sys.exit(0 if success else 1)
