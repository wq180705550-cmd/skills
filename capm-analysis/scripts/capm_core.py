"""
CAPM 核心计算模块（修复版）

修复原仓库的缺陷：
1. 使用 statsmodels.OLS 代替 np.polyfit（准确计算 Beta）
2. 自动获取无风险利率（10年期国债收益率）
3. 支持多市场基准（沪深300、中证500、S&P 500 等）
4. 增加模型诊断（R²、残差分析、显著性检验）
"""

import sys
import json
import argparse
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

# 尝试导入 statsmodels（用于稳健线性回归）
try:
    import statsmodels.api as sm
    HAS_STATSMODELS = True
except ImportError:
    HAS_STATSMODELS = False
    print("警告：未安装 statsmodels，将使用 numpy.polyfit（不推荐）")
    print("安装命令：pip install statsmodels")

# 尝试导入 yfinance（用于获取美股数据）
try:
    import yfinance as yf
    HAS_YFINANCE = True
except ImportError:
    HAS_YFINANCE = False

# 尝试导入 akshare（用于获取 A股数据）
try:
    import akshare as ak
    HAS_AKSHARE = True
except ImportError:
    HAS_AKSHARE = False


def get_risk_free_rate(
    market: str = 'CN',
    tenor: str = '10Y',
    date: Optional[str] = None
) -> float:
    """
    获取无风险利率
    
    Args:
        market: 市场（'CN' = 中国，'US' = 美国）
        tenor: 期限（'10Y' = 10年期，'1Y' = 1年期，'3M' = 3个月，'1M' = 1个月）
        date: 日期（YYYY-MM-DD），默认为今天
    
    Returns:
        无风险利率（年化，小数形式）
    
    Examples:
        >>> get_risk_free_rate('CN', '10Y')
        0.025  # 2.5%
        
        >>> get_risk_free_rate('US', '10Y')
        0.045  # 4.5%
    """
    if market == 'CN':
        # 中国无风险利率：10年期国债收益率
        # 尝试从 akshare 获取
        if HAS_AKSHARE:
            try:
                # 获取国债收益率数据
                df = ak.bond_zh_us_rate()
                # 筛选10年期国债
                tenor_map = {'10Y': '10年', '1Y': '1年', '3M': '3个月', '1M': '1个月'}
                target_tenor = tenor_map.get(tenor, '10年')
                
                rate_row = df[df['期限'].str.contains(target_tenor)]
                if not rate_row.empty:
                    rate = float(rate_row.iloc[0]['收益率']) / 100  # 转换为小数
                    print(f"中国{tenor}国债收益率：{rate:.2%}")
                    return rate
            except Exception as e:
                print(f"从 akshare 获取国债收益率失败：{e}")
        
        # 默认值（中国 10年期国债收益率约为 2.5%）
        default_rates = {'10Y': 0.025, '1Y': 0.020, '3M': 0.018, '1M': 0.015}
        default_rate = default_rates.get(tenor, 0.025)
        print(f"使用默认中国无风险利率：{default_rate:.2%}")
        return default_rate
    
    elif market == 'US':
        # 美国无风险利率：10年期国债收益率
        # 尝试从 FRED API 获取（需要 pandas-datareader）
        try:
            from pandas_datareader import DataReader
            if date is None:
                date = datetime.today().strftime('%Y-%m-%d')
            start_date = (datetime.strptime(date, '%Y-%m-%d') - timedelta(days=7)).strftime('%Y-%m-%d')
            
            # FRED 代码：DGS10 = 10-Year Treasury Constant Maturity Rate
            tenor_code_map = {
                '10Y': 'DGS10',
                '1Y': 'DGS1',
                '3M': 'DGS3MO',
                '1M': 'DGS1MO'
            }
            series_code = tenor_code_map.get(tenor, 'DGS10')
            
            df = DataReader(series_code, 'fred', start_date, date)
            if not df.empty:
                rate = float(df.iloc[-1].values[0]) / 100  # 转换为小数
                print(f"美国{tenor}国债收益率：{rate:.2%}")
                return rate
        except Exception as e:
            print(f"从 FRED 获取国债收益率失败：{e}")
        
        # 默认值（美国 10年期国债收益率约为 4.5%）
        default_rates = {'10Y': 0.045, '1Y': 0.040, '3M': 0.035, '1M': 0.030}
        default_rate = default_rates.get(tenor, 0.045)
        print(f"使用默认美国无风险利率：{default_rate:.2%}")
        return default_rate
    
    else:
        raise ValueError(f"不支持的市场：{market}")


def get_market_data(
    benchmark: str = '000300.SH',
    start_date: str = '2023-01-01',
    end_date: str = '2023-12-31',
    frequency: str = 'daily'
) -> pd.DataFrame:
    """
    获取市场基准数据
    
    Args:
        benchmark: 市场基准代码
            - '000300.SH' = 沪深300
            - '000905.SH' = 中证500
            - 'HSI' = 恒生指数
            - '^GSPC' = S&P 500
        start_date: 开始日期（YYYY-MM-DD）
        end_date: 结束日期（YYYY-MM-DD）
        frequency: 数据频率（'daily' = 日度，'weekly' = 周度，'monthly' = 月度）
    
    Returns:
        市场基准价格数据（DataFrame，索引为日期）
    """
    # 判断市场
    if benchmark.endswith('.SH') or benchmark.endswith('.SZ'):
        # A股市场基准
        if HAS_AKSHARE:
            try:
                # 使用 akshare 获取指数数据
                benchmark_symbol = benchmark.replace('.SH', '').replace('.SZ', '')
                df = ak.stock_zh_index_daily(symbol=benchmark_symbol)
                df['date'] = pd.to_datetime(df['date'])
                df = df.set_index('date')
                df = df.loc[start_date:end_date]
                
                if frequency == 'weekly':
                    df = df.resample('W').last()
                elif frequency == 'monthly':
                    df = df.resample('M').last()
                
                print(f"成功获取市场基准数据：{benchmark}（{len(df)} 条记录）")
                return df[['close']]
            except Exception as e:
                print(f"从 akshare 获取市场基准数据失败：{e}")
                raise
        else:
            raise ImportError("需要安装 akshare：pip install akshare")
    
    else:
        # 美股/港股市场基准
        if HAS_YFINANCE:
            try:
                ticker = yf.Ticker(benchmark)
                df = ticker.history(start=start_date, end=end_date)
                
                if frequency == 'weekly':
                    df = df.resample('W').last()
                elif frequency == 'monthly':
                    df = df.resample('M').last()
                
                print(f"成功获取市场基准数据：{benchmark}（{len(df)} 条记录）")
                return df[['Close']].rename(columns={'Close': 'close'})
            except Exception as e:
                print(f"从 yfinance 获取市场基准数据失败：{e}")
                raise
        else:
            raise ImportError("需要安装 yfinance：pip install yfinance")


def get_stock_data(
    stock: str,
    start_date: str = '2023-01-01',
    end_date: str = '2023-12-31',
    frequency: str = 'daily',
    use_westock: bool = False
) -> pd.DataFrame:
    """
    获取股票数据
    
    Args:
        stock: 股票代码
        start_date: 开始日期（YYYY-MM-DD）
        end_date: 结束日期（YYYY-MM-DD）
        frequency: 数据频率
        use_westock: 是否使用 westock-data（需要在 WorkBuddy 环境中运行）
    
    Returns:
        股票价格数据（DataFrame，索引为日期）
    """
    if use_westock:
        # 提示：需要在 WorkBuddy 中调用 westock-data skill
        print("提示：使用 westock-data 获取数据需要在 WorkBuddy 中调用")
        print("请先运行：@skill:westock-data 获取股票日度价格数据")
        raise NotImplementedError("westock-data 集成需要在 WorkBuddy 对话中完成")
    
    # 使用 akshare（A股）或 yfinance（美股/港股）
    if stock.endswith('.SH') or stock.endswith('.SZ'):
        # A股
        if HAS_AKSHARE:
            try:
                symbol = stock.replace('.SH', '').replace('.SZ', '')
                df = ak.stock_zh_a_hist(
                    symbol=symbol,
                    start_date=start_date.replace('-', ''),
                    end_date=end_date.replace('-', ''),
                    adjust="qfq"  # 前复权
                )
                df['日期'] = pd.to_datetime(df['日期'])
                df = df.set_index('日期')
                df = df.loc[start_date:end_date]
                
                if frequency == 'weekly':
                    df = df.resample('W').last()
                elif frequency == 'monthly':
                    df = df.resample('M').last()
                
                print(f"成功获取股票数据：{stock}（{len(df)} 条记录）")
                return df[['收盘']].rename(columns={'收盘': 'close'})
            except Exception as e:
                print(f"从 akshare 获取股票数据失败：{e}")
                raise
        else:
            raise ImportError("需要安装 akshare：pip install akshare")
    
    else:
        # 美股/港股
        if HAS_YFINANCE:
            try:
                ticker = yf.Ticker(stock)
                df = ticker.history(start=start_date, end=end_date)
                
                if frequency == 'weekly':
                    df = df.resample('W').last()
                elif frequency == 'monthly':
                    df = df.resample('M').last()
                
                print(f"成功获取股票数据：{stock}（{len(df)} 条记录）")
                return df[['Close']].rename(columns={'Close': 'close'})
            except Exception as e:
                print(f"从 yfinance 获取股票数据失败：{e}")
                raise
        else:
            raise ImportError("需要安装 yfinance：pip install yfinance")


def calculate_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """
    计算收益率
    
    Args:
        prices: 价格数据（DataFrame，索引为日期，列为股票代码或指数代码）
    
    Returns:
        收益率数据（DataFrame，与输入同维度，首行为 NaN）
    """
    # 计算对数收益率（更符合金融理论）
    returns = np.log(prices / prices.shift(1))
    
    # 或者计算简单收益率（与原仓库一致）
    # returns = prices.pct_change()
    
    return returns.dropna()


def calculate_beta(
    stock_returns: pd.Series,
    market_returns: pd.Series,
    risk_free_rate: float,
    use_ols: bool = True
) -> Dict:
    """
    计算 Beta 系数（修复版）
    
    Args:
        stock_returns: 股票收益率序列
        market_returns: 市场收益率序列
        risk_free_rate: 无风险利率（年化，小数形式）
        use_ols: 是否使用 OLS 回归（推荐）
    
    Returns:
        包含 Beta、Alpha、R²、p 值等的字典
    
    Examples:
        >>> result = calculate_beta(stock_ret, market_ret, 0.025)
        >>> print(f"Beta: {result['beta']:.4f}")
        >>> print(f"R²: {result['r_squared']:.4f}")
    """
    # 对齐数据（确保索引一致）
    df = pd.DataFrame({
        'stock_return': stock_returns,
        'market_return': market_returns
    }).dropna()
    
    if len(df) < 30:
        raise ValueError(f"数据点数不足（仅 {len(df)} 条），无法可靠估计 Beta")
    
    # 计算超额收益率
    df['stock_excess'] = df['stock_return'] - risk_free_rate / 252  # 日度无风险利率
    df['market_excess'] = df['market_return'] - risk_free_rate / 252
    
    if use_ols and HAS_STATSMODELS:
        # 方法一：使用 statsmodels.OLS（推荐）
        X = df['market_excess']
        X = sm.add_constant(X)  # 添加常数项（用于估计 Alpha）
        y = df['stock_excess']
        
        model = sm.OLS(y, X).fit()
        
        beta = model.params['market_excess']
        alpha = model.params['const'] * 252  # 转换为年化
        r_squared = model.rsquared
        p_value = model.pvalues['market_excess']
        std_error = model.bse['market_excess']
        
        # 模型诊断
        residuals = model.resid
        fitted_values = model.fittedvalues
        
        result = {
            'beta': float(beta),
            'alpha': float(alpha),
            'r_squared': float(r_squared),
            'p_value': float(p_value),
            'std_error': float(std_error),
            't_statistic': float(beta / std_error),
            'n_observations': len(df),
            'residuals': residuals.values.tolist(),
            'fitted_values': fitted_values.values.tolist(),
            'method': 'OLS'
        }
        
        # 打印回归结果
        print("\n" + "="*60)
        print("CAPM 回归结果（OLS）")
        print("="*60)
        print(f"Beta（β）: {beta:.4f}")
        print(f"Alpha（α，年化）: {alpha:.4f} ({alpha*100:.2f}%)")
        print(f"R²: {r_squared:.4f}")
        print(f"Beta p 值: {p_value:.4f}" + (" *" if p_value < 0.05 else ""))
        print(f"Beta 标准误: {std_error:.4f}")
        print(f"t 统计量: {beta/std_error:.4f}")
        print(f"观测值数量: {len(df)}")
        print("="*60)
        
    else:
        # 方法二：使用 numpy.polyfit（不推荐，仅作为备选）
        print("警告：使用 numpy.polyfit 计算 Beta（不准确）")
        print("建议安装 statsmodels：pip install statsmodels")
        
        x = df['market_excess'].values
        y = df['stock_excess'].values
        
        b, a = np.polyfit(x, y, 1)
        
        # 计算 R²
        y_pred = b * x + a
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1 - (ss_res / ss_tot)
        
        result = {
            'beta': float(b),
            'alpha': float(a * 252),  # 转换为年化
            'r_squared': float(r_squared),
            'p_value': np.nan,
            'std_error': np.nan,
            't_statistic': np.nan,
            'n_observations': len(df),
            'method': 'polyfit'
        }
        
        print("\n" + "="*60)
        print("CAPM 回归结果（polyfit）")
        print("="*60)
        print(f"Beta（β）: {b:.4f}")
        print(f"Alpha（α，年化）: {a*252:.4f} ({a*252*100:.2f}%)")
        print(f"R²: {r_squared:.4f}")
        print("="*60)
    
    return result


def calculate_expected_return(
    beta: float,
    market_return: float,
    risk_free_rate: float
) -> float:
    """
    计算预期收益率（CAPM 公式）
    
    Args:
        beta: Beta 系数
        market_return: 市场组合预期收益率（年化，小数形式）
        risk_free_rate: 无风险利率（年化，小数形式）
    
    Returns:
        股票预期收益率（年化，小数形式）
    
    Formula:
        E(R_i) = R_f + β × (E(R_m) - R_f)
    """
    expected_return = risk_free_rate + beta * (market_return - risk_free_rate)
    return expected_return


def run_capm_analysis(
    stock: str,
    benchmark: str = '000300.SH',
    start_date: str = '2023-01-01',
    end_date: str = '2023-12-31',
    risk_free_tenor: str = '10Y',
    frequency: str = 'daily',
    use_westock: bool = False
) -> Dict:
    """
    运行完整的 CAPM 分析
    
    Args:
        stock: 股票代码
        benchmark: 市场基准代码
        start_date: 开始日期
        end_date: 结束日期
        risk_free_tenor: 无风险利率期限
        frequency: 数据频率
        use_westock: 是否使用 westock-data
    
    Returns:
        包含完整分析结果的字典
    """
    print("\n" + "="*60)
    print("CAPM 分析")
    print("="*60)
    print(f"股票：{stock}")
    print(f"市场基准：{benchmark}")
    print(f"时间段：{start_date} 至 {end_date}")
    print(f"数据频率：{frequency}")
    print("="*60 + "\n")
    
    # 1. 获取无风险利率
    print("【步骤 1/5】获取无风险利率...")
    if benchmark.endswith('.SH') or benchmark.endswith('.SZ'):
        market = 'CN'
    else:
        market = 'US'
    
    risk_free_rate = get_risk_free_rate(market, risk_free_tenor)
    print(f"  无风险利率（{risk_free_tenor}）：{risk_free_rate:.2%}\n")
    
    # 2. 获取市场基准数据
    print("【步骤 2/5】获取市场基准数据...")
    market_prices = get_market_data(benchmark, start_date, end_date, frequency)
    market_returns = calculate_returns(market_prices)
    market_excess_return = (market_returns.mean() * 252 - risk_free_rate).values[0]  # 年化市场风险溢价
    print(f"  市场年化收益率：{market_returns.mean()*252:.2%}")
    print(f"  市场风险溢价：{market_excess_return:.2%}\n")
    
    # 3. 获取股票数据
    print("【步骤 3/5】获取股票数据...")
    stock_prices = get_stock_data(stock, start_date, end_date, frequency, use_westock)
    stock_returns = calculate_returns(stock_prices)
    print(f"  股票年化收益率：{stock_returns.mean()*252:.2%}\n")
    
    # 4. 计算 Beta
    print("【步骤 4/5】计算 Beta 系数...")
    beta_result = calculate_beta(
        stock_returns.iloc[:, 0],
        market_returns.iloc[:, 0],
        risk_free_rate
    )
    
    # 5. 计算预期收益率
    print("【步骤 5/5】计算预期收益率...")
    expected_return = calculate_expected_return(
        beta_result['beta'],
        market_returns.mean() * 252,
        risk_free_rate
    )
    print(f"  预期收益率（CAPM）：{expected_return:.2%}\n")
    
    # 汇总结果
    result = {
        'stock': stock,
        'benchmark': benchmark,
        'start_date': start_date,
        'end_date': end_date,
        'risk_free_rate': risk_free_rate,
        'risk_free_tenor': risk_free_tenor,
        'market_return': float(market_returns.mean() * 252),
        'market_excess_return': float(market_excess_return),
        'stock_return': float(stock_returns.mean() * 252),
        'beta': beta_result['beta'],
        'alpha': beta_result['alpha'],
        'r_squared': beta_result['r_squared'],
        'p_value': beta_result['p_value'],
        'std_error': beta_result['std_error'],
        'expected_return': expected_return,
        'n_observations': beta_result['n_observations'],
        'method': beta_result['method']
    }
    
    print("="*60)
    print("CAPM 分析结果汇总")
    print("="*60)
    print(f"Beta（β）: {result['beta']:.4f}")
    print(f"Alpha（α，年化）: {result['alpha']:.4f} ({result['alpha']*100:.2f}%)")
    print(f"预期收益率（CAPM）: {result['expected_return']:.2%}")
    print(f"R²: {result['r_squared']:.4f}")
    print(f"观测值数量: {result['n_observations']}")
    print("="*60 + "\n")
    
    return result


def main():
    """命令行接口"""
    parser = argparse.ArgumentParser(description='CAPM 分析')
    parser.add_argument('--stock', required=True, help='股票代码')
    parser.add_argument('--benchmark', default='000300.SH', help='市场基准代码')
    parser.add_argument('--start-date', default='2023-01-01', help='开始日期（YYYY-MM-DD）')
    parser.add_argument('--end-date', default='2023-12-31', help='结束日期（YYYY-MM-DD）')
    parser.add_argument('--risk-free-tenor', default='10Y', help='无风险利率期限')
    parser.add_argument('--frequency', default='daily', help='数据频率')
    parser.add_argument('--use-westock', action='store_true', help='使用 westock-data')
    parser.add_argument('--output', help='输出 JSON 文件路径')
    
    args = parser.parse_args()
    
    # 运行 CAPM 分析
    result = run_capm_analysis(
        args.stock,
        args.benchmark,
        args.start_date,
        args.end_date,
        args.risk_free_tenor,
        args.frequency,
        args.use_westock
    )
    
    # 保存结果
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"结果已保存到：{args.output}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
