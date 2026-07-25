"""
单只股票 CAPM 计算脚本

命令行接口，用于计算单只股票的 CAPM 指标。
"""

import sys
import json
import argparse
import pandas as pd
from typing import Dict

# 导入 CAPM 核心计算模块
sys.path.insert(0, '.')
from capm_core import run_capm_analysis


def main():
    parser = argparse.ArgumentParser(description='单只股票 CAPM 计算')
    parser.add_argument('--stock', required=True, help='股票代码')
    parser.add_argument('--benchmark', default='000300.SH', help='市场基准代码')
    parser.add_argument('--start-date', default='2023-01-01', help='开始日期（YYYY-MM-DD）')
    parser.add_argument('--end-date', default='2023-12-31', help='结束日期（YYYY-MM-DD）')
    parser.add_argument('--risk-free-tenor', default='10Y', help='无风险利率期限')
    parser.add_argument('--frequency', default='daily', help='数据频率')
    parser.add_argument('--use-westock', action='store_true', help='使用 westock-data')
    parser.add_argument('--output', help='输出 JSON 文件路径')
    parser.add_argument('--plot', action='store_true', help='生成散点图')
    
    args = parser.parse_args()
    
    # 运行 CAPM 分析
    result = run_capm_analysis(
        stock=args.stock,
        benchmark=args.benchmark,
        start_date=args.start_date,
        end_date=args.end_date,
        risk_free_tenor=args.risk_free_tenor,
        frequency=args.frequency,
        use_westock=args.use_westock
    )
    
    # 生成散点图（如果指定）
    if args.plot:
        try:
            import matplotlib.pyplot as plt
            
            # 重新获取收益率数据（用于绘图）
            from capm_core import get_market_data, get_stock_data, calculate_returns
            
            market_returns = calculate_returns(get_market_data(
                args.benchmark, args.start_date, args.end_date, args.frequency
            ))
            stock_returns = calculate_returns(get_stock_data(
                args.stock, args.start_date, args.end_date, args.frequency, args.use_westock
            ))
            
            # 对齐数据
            df_plot = pd.DataFrame({
                'market_return': market_returns.iloc[:, 0],
                'stock_return': stock_returns.iloc[:, 0]
            }).dropna()
            
            # 绘制散点图
            plt.figure(figsize=(10, 6))
            plt.scatter(df_plot['market_return'], df_plot['stock_return'], alpha=0.6)
            
            # 添加回归线
            beta = result['beta']
            alpha = result['alpha'] / 252  # 转换为日度
            x_line = np.linspace(df_plot['market_return'].min(), df_plot['market_return'].max(), 100)
            y_line = alpha + beta * x_line
            plt.plot(x_line, y_line, 'r-', linewidth=2, label=f'Beta = {beta:.4f}')
            
            plt.xlabel('Market Return')
            plt.ylabel('Stock Return')
            plt.title(f'{args.stock}: Stock Return vs Market Return')
            plt.legend()
            plt.grid(True, alpha=0.3)
            
            # 保存图片
            plot_file = f"capm_scatter_{args.stock.replace('.', '_')}.png"
            plt.savefig(plot_file, dpi=300, bbox_inches='tight')
            print(f"\n散点图已保存：{plot_file}")
            
        except ImportError:
            print("\n提示：安装 matplotlib 以生成图表：pip install matplotlib")
    
    # 保存结果
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\n结果已保存到：{args.output}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
