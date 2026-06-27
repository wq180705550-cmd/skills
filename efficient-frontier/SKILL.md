---
name: efficient-frontier
description: >
  基于现代投资组合理论（MPT）的有效前沿计算与投资组合优化工具。
  支持A股市场股票数据获取、收益率计算、协方差矩阵估计、投资组合优化、
  有效前沿绘制等功能。适用于量化投资、资产配置、风险管理等场景。
  触发场景：用户提到「投资组合优化」、「有效前沿」、「资产配置」、
  「夏普比率」、「最小化风险」、「最大化收益」等。
agent_created: true
---

# Efficient Frontier — 投资组合有效前沿

基于 Modern Portfolio Theory (MPT) 的投资组合优化工具，实现 Markowitz 有效前沿计算。

## 核心概念

### 现代投资组合理论（MPT）核心思想

1. **风险-收益权衡**：投资者是风险厌恶的，承担更高风险需要更高的预期收益补偿
2. **分散化价值**：投资组合的风险不等于组合内个股风险的加权平均，而是取决于资产之间的相关性
3. **有效前沿**：在所有"给定风险水平下收益最高、或给定收益水平下风险最低"的投资组合构成的边界

### 关键公式

**组合预期收益率**：
$$E(R_p) = \sum_{i=1}^n w_i E(R_i)$$

**组合风险（方差）**：
$$\sigma_p^2 = \mathbf{w}^T \mathbf{\Sigma} \mathbf{w}$$

**夏普比率**：
$$Sharpe\ Ratio = \frac{E(R_p) - R_f}{\sigma_p}$$

其中：
- $w_i$：资产 i 的权重
- $E(R_i)$：资产 i 的预期收益率
- $\mathbf{\Sigma}$：资产收益率的协方差矩阵
- $R_f$：无风险利率

---

## 工作流

### 第 1 步：数据获取与预处理

#### A股市场数据获取

使用 `westock-data` skill 或 `akshare` 库获取A股股票数据：

```python
import akshare as ak
import pandas as pd
import numpy as np

def fetch_stock_data(stocks, start_date, end_date):
    """
    获取A股股票日度调整后收盘价
    
    Args:
        stocks: 股票代码列表，如 ['600519.SH', '000858.SZ']
        start_date: 开始日期，格式 'YYYYMMDD'
        end_date: 结束日期，格式 'YYYYMMDD'
    
    Returns:
        DataFrame: 宽表格式，索引为日期，列为股票代码
    """
    data = {}
    for stock in stocks:
        # 使用 akshare 获取日度数据
        df = ak.stock_zh_a_hist(
            symbol=stock.replace('.SH', '').replace('.SZ', ''),
            start_date=start_date,
            end_date=end_date,
            adjust="qfq"  # 前复权
        )
        data[stock] = df.set_index('日期')['收盘']
    
    # 合并为宽表
    price_data = pd.DataFrame(data)
    return price_data
```

**推荐使用 `westock-data` skill**（已针对A股优化）：

```
使用 @skill:westock-data 获取股票日度价格数据
参数：
  - 股票代码：如 600519.SH（贵州茅台）、000858.SZ（五粮液）
  - 字段：close（收盘价）
  - 频率：daily
  - 复权：前复权（qfq）
```

#### 数据预处理

```python
def preprocess_data(price_data):
    """
    预处理价格数据：处理缺失值、计算收益率
    
    Args:
        price_data: DataFrame，索引为日期，列为股票代码
        
    Returns:
        returns: DataFrame，日度对数收益率
        annual_returns: Series，年化收益率
        cov_matrix: DataFrame，年化协方差矩阵
    """
    # 1. 删除交易天数不足的股票（如上市不足1年）
    min_trading_days = 252  # 约1年
    valid_stocks = price_data.columns[price_data.notna().sum() >= min_trading_days]
    price_data = price_data[valid_stocks]
    
    # 2. 填充缺失值（使用前向填充）
    price_data = price_data.fillna(method='ffill')
    
    # 3. 计算对数收益率
    returns = np.log(price_data / price_data.shift(1)).dropna()
    
    # 4. 转换为年化收益率（假设一年252个交易日）
    annual_returns = returns.mean() * 252
    
    # 5. 计算年化协方差矩阵
    cov_matrix = returns.cov() * 252
    
    return returns, annual_returns, cov_matrix
```

---

### 第 2 步：投资组合优化

使用 `scipy.optimize` 实现两类优化：

#### 2.1 最小化风险（给定目标收益率）

```python
import scipy.optimize as sco

def minimize_risk(target_return, annual_returns, cov_matrix, allow_short=False):
    """
    在给定目标收益率下，最小化投资组合风险
    
    Args:
        target_return: 目标年化收益率
        annual_returns: Series，年化收益率
        cov_matrix: DataFrame，年化协方差矩阵
        allow_short: 是否允许做空（权重为负）
    
    Returns:
        dict: 最优权重、预期收益率、风险（波动率）、夏普比率
    """
    n_assets = len(annual_returns)
    
    # 目标函数：最小化组合方差
    def portfolio_variance(weights):
        return np.dot(weights.T, np.dot(cov_matrix, weights))
    
    # 约束条件
    constraints = [
        {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},  # 权重之和为1
        {'type': 'eq', 'fun': lambda x: np.dot(x, annual_returns) - target_return}  # 达到目标收益率
    ]
    
    # 边界条件
    if allow_short:
        bounds = tuple((-1, 1) for _ in range(n_assets))  # 允许做空
    else:
        bounds = tuple((0, 1) for _ in range(n_assets))  # 不允许做空
    
    # 初始猜测：等权重
    initial_guess = np.array([1.0 / n_assets] * n_assets)
    
    # 优化
    result = sco.minimize(
        portfolio_variance,
        initial_guess,
        method='SLSQP',
        bounds=bounds,
        constraints=constraints
    )
    
    if not result.success:
        raise ValueError("优化失败，请检查约束条件")
    
    optimal_weights = result.x
    portfolio_return = np.dot(optimal_weights, annual_returns)
    portfolio_risk = np.sqrt(result.fun)
    sharpe_ratio = portfolio_return / portfolio_risk  # 假设无风险利率为0
    
    return {
        'weights': optimal_weights,
        'return': portfolio_return,
        'risk': portfolio_risk,
        'sharpe_ratio': sharpe_ratio
    }
```

#### 2.2 最大化夏普比率

```python
def maximize_sharpe(annual_returns, cov_matrix, risk_free_rate=0.025, allow_short=False):
    """
    最大化夏普比率
    
    Args:
        annual_returns: Series，年化收益率
        cov_matrix: DataFrame，年化协方差矩阵
        risk_free_rate: 无风险利率（默认2.5%，对应10年期国债收益率）
        allow_short: 是否允许做空
    
    Returns:
        dict: 最优权重、预期收益率、风险（波动率）、夏普比率
    """
    n_assets = len(annual_returns)
    
    # 目标函数：最小化夏普比率的负值（即最大化夏普比率）
    def negative_sharpe(weights):
        portfolio_return = np.dot(weights, annual_returns)
        portfolio_risk = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        return -(portfolio_return - risk_free_rate) / portfolio_risk
    
    # 约束条件：权重之和为1
    constraints = {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}
    
    # 边界条件
    if allow_short:
        bounds = tuple((-1, 1) for _ in range(n_assets))
    else:
        bounds = tuple((0, 1) for _ in range(n_assets))
    
    # 初始猜测：等权重
    initial_guess = np.array([1.0 / n_assets] * n_assets)
    
    # 优化
    result = sco.minimize(
        negative_sharpe,
        initial_guess,
        method='SLSQP',
        bounds=bounds,
        constraints=constraints
    )
    
    if not result.success:
        raise ValueError("优化失败，请检查约束条件")
    
    optimal_weights = result.x
    portfolio_return = np.dot(optimal_weights, annual_returns)
    portfolio_risk = np.sqrt(np.dot(optimal_weights.T, np.dot(cov_matrix, optimal_weights)))
    sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_risk
    
    return {
        'weights': optimal_weights,
        'return': portfolio_return,
        'risk': portfolio_risk,
        'sharpe_ratio': sharpe_ratio
    }
```

---

### 第 3 步：计算有效前沿

```python
def calculate_efficient_frontier(annual_returns, cov_matrix, n_points=100, allow_short=False):
    """
    计算有效前沿上的点
    
    Args:
        annual_returns: Series，年化收益率
        cov_matrix: DataFrame，年化协方差矩阵
        n_points: 有效前沿上的点数
        allow_short: 是否允许做空
    
    Returns:
        tuple: (风险列表, 收益率列表)
    """
    # 确定目标收益率范围
    min_return = annual_returns.min()
    max_return = annual_returns.max()
    target_returns = np.linspace(min_return, max_return, n_points)
    
    efficient_portfolios = []
    for target_return in target_returns:
        try:
            portfolio = minimize_risk(target_return, annual_returns, cov_matrix, allow_short)
            efficient_portfolios.append(portfolio)
        except ValueError:
            continue
    
    # 提取风险和收益率
    risks = [p['risk'] for p in efficient_portfolios]
    returns = [p['return'] for p in efficient_portfolios]
    
    return risks, returns
```

---

### 第 4 步：可视化有效前沿

```python
import matplotlib.pyplot as plt

def plot_efficient_frontier(returns, cov_matrix, n_random=5000, allow_short=False):
    """
    绘制有效前沿和蒙特卡洛模拟散点
    
    Args:
        returns: Series，年化收益率
        cov_matrix: DataFrame，年化协方差矩阵
        n_random: 蒙特卡洛模拟的随机组合数量
        allow_short: 是否允许做空
    """
    # 1. 蒙特卡洛模拟：生成随机权重组合
    n_assets = len(returns)
    random_returns = []
    random_risks = []
    
    for _ in range(n_random):
        if allow_short:
            weights = np.random.uniform(-1, 1, n_assets)
        else:
            weights = np.random.random(n_assets)
        weights /= np.sum(weights)  # 归一化
        
        portfolio_return = np.dot(weights, returns)
        portfolio_risk = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        
        random_returns.append(portfolio_return)
        random_risks.append(portfolio_risk)
    
    # 2. 计算有效前沿
    efficient_risks, efficient_returns = calculate_efficient_frontier(
        returns, cov_matrix, allow_short=allow_short
    )
    
    # 3. 计算最大夏普比率组合
    max_sharpe_portfolio = maximize_sharpe(returns, cov_matrix, allow_short=allow_short)
    
    # 4. 绘图
    plt.figure(figsize=(12, 8))
    
    # 随机组合散点
    plt.scatter(random_risks, random_returns, c='lightgray', alpha=0.3, s=10, label='随机组合')
    
    # 有效前沿曲线
    plt.plot(efficient_risks, efficient_returns, 'b-', linewidth=3, label='有效前沿')
    
    # 最大夏普比率组合
    plt.scatter(
        max_sharpe_portfolio['risk'],
        max_sharpe_portfolio['return'],
        c='red',
        s=100,
        marker='*',
        label=f'最大夏普比率 (SR={max_sharpe_portfolio["sharpe_ratio"]:.2f})'
    )
    
    plt.xlabel('风险（年化波动率）', fontsize=12)
    plt.ylabel('预期收益率（年化）', fontsize=12)
    plt.title('投资组合有效前沿', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=10)
    
    # 显示数值
    print(f"最大夏普比率组合：")
    print(f"  预期收益率：{max_sharpe_portfolio['return']:.2%}")
    print(f"  风险（波动率）：{max_sharpe_portfolio['risk']:.2%}")
    print(f"  夏普比率：{max_sharpe_portfolio['sharpe_ratio']:.2f}")
    print(f"\n权重分配：")
    for stock, weight in zip(returns.index, max_sharpe_portfolio['weights']):
        print(f"  {stock}: {weight:.2%}")
    
    plt.show()
```

---

## 完整示例

### 场景：优化A股消费板块投资组合

```python
# 1. 定义股票池（消费板块龙头）
stocks = ['600519.SH', '000858.SZ', '603288.SH', '600887.SH']  # 茅台、五粮液、海天味业、伊利股份
start_date = '20230101'
end_date = '20231231'

# 2. 获取数据
price_data = fetch_stock_data(stocks, start_date, end_date)

# 3. 预处理
returns, annual_returns, cov_matrix = preprocess_data(price_data)

print("年化收益率：")
print(annual_returns)
print("\n年化协方差矩阵：")
print(cov_matrix)

# 4. 计算最大夏普比率组合
max_sharpe = maximize_sharpe(annual_returns, cov_matrix, risk_free_rate=0.025)
print(f"\n最大夏普比率组合：")
print(f"  预期收益率：{max_sharpe['return']:.2%}")
print(f"  风险（波动率）：{max_sharpe['risk']:.2%}")
print(f"  夏普比率：{max_sharpe['sharpe_ratio']:.2f}")

# 5. 绘制有效前沿
plot_efficient_frontier(annual_returns, cov_matrix)
```

---

## A股市场适配注意事项

### 1. 数据质量

- **停牌处理**：A股股票可能长期停牌，需要剔除停牌时间过长的股票
- **涨跌停限制**：A股有±10%（ST股票±5%）的涨跌停限制，影响收益率分布
- **复权处理**：必须使用前复权价格，否则分红除权会影响收益率计算

### 2. 卖空限制

- A股市场普通投资者无法做空个股，优化时应设置 `allow_short=False`
- 可通过融券卖出，但成本高且标的有限

### 3. 交易成本

- 印花税：0.1%（卖出时征收）
- 佣金：约0.025%（双向征收）
- 在优化时应考虑换手率约束，避免过于频繁调仓

### 4. 无风险利率

- 推荐使用10年期国债收益率作为无风险利率
- 当前（2026年6月）约为2.5%

---

## 进阶功能

### 1. 加入约束条件

```python
# 示例：限制单个股票权重不超过30%
constraints = [
    {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
    {'type': 'ineq', 'fun': lambda x: 0.3 - x}  # 每个权重不超过0.3
]

# 示例：限制组合换手率
# 需要传入上一个周期的权重，计算 turnover 约束
```

### 2. 使用 Black-Litterman 模型

- 结合市场均衡收益率和投资者主观观点
- 更适合机构投资者的资产配置

### 3. 风险平价（Risk Parity）策略

- 不再追求最大化夏普比率，而是让每个资产对组合风险的贡献相等
- 更适合风险分散化需求

---

## 常见问题排查

### 优化失败（constraints not satisfied）

**原因**：
1. 目标收益率超出可行范围（高于最高收益股票或低于最低收益股票）
2. 协方差矩阵奇异（股票收益率完全相关）

**修复**：
1. 检查 `annual_returns` 的范围，确保目标收益率在合理区间内
2. 使用正则化协方差矩阵：`cov_matrix + np.eye(n) * 1e-6`

### 权重集中在单只股票

**原因**：该股票明显优于其他股票（高收益低波动）

**修复**：
1. 加入权重上限约束（如单只股票不超过30%）
2. 使用风险平价策略
3. 扩大股票池，增加分散化空间

---

## 依赖库

```python
# 必需库
import pandas as pd
import numpy as np
import scipy.optimize as sco
import matplotlib.pyplot as plt

# A股数据获取（二选一）
import akshare as ak  # 免费，数据质量一般
# 或者使用 westock-data skill（推荐，数据质量高）

# 可选：风险平价、Black-Litterman 等进阶功能
# pip install riskparityportfolio
```

---

## 默认表述

启动本 skill 时，向用户说明分析计划：

> 「我将基于现代投资组合理论（MPT）为您优化投资组合。
> 
> 分析步骤：
> 1. 获取股票池的价格数据（使用 westock-data 或 akshare）
> 2. 计算对数收益率和协方差矩阵
> 3. 优化投资组合（最小化风险 / 最大化夏普比率）
> 4. 绘制有效前沿曲线
> 
> 需要您提供：
> - 股票池（如：消费板块龙头）
> - 分析时间段
> - 是否允许做空（默认不允许）
> - 无风险利率（默认2.5%）」
