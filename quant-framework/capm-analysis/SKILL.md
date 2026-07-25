---
name: capm-analysis
description: >
  统一量化分析框架：CAPM（资本资产定价模型）+ 多因子打分 + 投资组合优化。
  支持A股/美股/港股适配、交互式Web应用、量化框架集成。
  修复了原仓库的Beta计算不准确、无风险利率固定、市场基准单一、缺少模型诊断等缺陷。
  触发场景：用户提到「CAPM」、「贝塔系数」、「多因子打分」、「投资组合优化」、
  「预期收益率」、「系统风险」、「量化因子」、「夏普比率」等。
agent_created: true
version: "2.0"
---

# CAPM Analysis v2.0 — 统一量化分析框架

CAPM + 多因子打分 + 投资组合优化的统一框架，支持A股/美股/港股。

---

## 核心功能

### 1. CAPM 计算（修复版）✅

**修复的缺陷**：

| 原仓库缺陷 | 修复方案 | 状态 |
|------------|----------|------|
| Beta 计算不准确（`np.polyfit`） | 使用 `statsmodels.OLS` 进行稳健线性回归 | ✅ |
| 无风险利率固定（4.5%） | 自动获取当前无风险利率（10年期国债收益率） | ✅ |
| 市场基准单一（仅 S&P 500） | 支持多市场基准（沪深300、中证500、恒生指数、S&P 500） | ✅ |
| 缺少模型诊断 | 增加 R²、残差分析、显著性检验 | ✅ |

**计算步骤**：

1. **获取无风险利率**（`get_risk_free_rate()`）
2. **获取市场基准数据**（`get_market_data()`）
3. **计算 Beta 系数**（`calculate_beta()`）
4. **计算预期收益率**（`calculate_expected_return()`）

---

### 2. 多因子打分系统 ✅ (新增)

**因子类别和默认权重**：

| 因子类别 | 默认权重 | 说明 |
|---------|---------|------|
| Momentum（动量） | 20% | 价格动量、多期收益率 |
| Technical（技术指标） | 15% | RSI、MACD、布林带、移动平均 |
| Volume（成交量） | 10% | 成交量变化、量价背离 |
| Fundamentals（基本面） | 20% | P/E、P/B、ROE、营收增长 |
| Macro（宏观经济） | 10% | 利率、CPI、PMI、货币政策 |
| Sector（行业板块） | 10% | 行业轮动、相对强度 |
| CAPM_Beta（系统风险） | 15% | Beta 系数（来自 CAPM 计算） |

**自定义权重**：

用户可以通过配置文件修改因子权重：

```python
factor_weights = {
    'momentum': 0.20,
    'technical': 0.15,
    'volume': 0.10,
    'fundamental': 0.20,
    'macro': 0.10,
    'sector': 0.10,
    'capm_beta': 0.15  # 新增：CAPM Beta 因子
}
```

**评分方法**：

每个因子标准化为 0-100 分，然后加权求和得到综合得分。

---

### 3. 投资组合优化 ✅ (整合 efficient-frontier)

**优化目标**：

1. **最小化风险**（给定目标收益率）
2. **最大化夏普比率**
3. **最大化预期收益率**（给定风险约束）

**输入**：

- 预期收益率（来自 CAPM 或用户指定）
- 协方差矩阵（来自历史收益率）
- 无风险利率
- 约束条件（不允许做空、行业权重上限等）

**输出**：

- 最优权重分配
- 预期收益率
- 风险（波动率）
- 夏普比率

---

### 4. 交互式 Web 应用 ✅

**技术栈**：Streamlit

**功能**：

1. **侧边栏配置**：
   - 选择分析模式（CAPM 计算 / 多因子打分 / 投资组合优化）
   - 选择市场（A股 / 美股 / 港股）
   - 选择市场基准（沪深300 / 中证500 / S&P 500 / ...）
   - 输入股票代码（支持多只）
   - 选择时间段
   - 调整因子权重（多因子打分模式）
   - 设置优化目标（投资组合优化模式）

2. **主界面展示**：
   - **CAPM 模式**：Beta、Alpha、R²、预期收益率、散点图、SML、模型诊断
   - **多因子打分模式**：因子得分热力图、综合得分排名、交易信号
   - **投资组合优化模式**：有效前沿曲线、最优权重分配、预期风险收益

---

## 安装依赖

```bash
# 核心依赖
pip install pandas numpy statsmodels yfinance pandas-datareader streamlit plotly scipy

# A股数据源（可选）
pip install akshare

# 技术分析（可选）
pip install ta

# 如果已安装 westock-data skill，可以调用它获取数据
```

---

## 使用方式

### 方式一：交互式 Web 应用（推荐）

```bash
streamlit run app/capm_app.py
```

**访问**：浏览器打开 `http://localhost:8501`

---

### 方式二：命令行脚本

```bash
# 1. CAPM 计算
python scripts/capm_core.py \
  --stock 600519.SH \
  --market-benchmark 000300.SH \
  --start-date 2023-01-01 \
  --end-date 2023-12-31

# 2. 多因子打分
python scripts/multi_factor_core.py \
  --stocks 600519.SH 000858.SZ 603288.SH \
  --start-date 2023-01-01 \
  --end-date 2023-12-31 \
  --config config/factor_weights.yaml

# 3. 投资组合优化
python scripts/optimize_portfolio.py \
  --stocks 600519.SH 000858.SZ 603288.SH 600887.SH \
  --start-date 2023-01-01 \
  --end-date 2023-12-31 \
  --risk-free-rate 0.025 \
  --target-return 0.15
```

---

### 方式三：在 WorkBuddy 中调用

```
@skill:capm-analysis

完整量化分析流程：
1. 计算消费板块股票的 CAPM（Beta、预期收益率）
2. 计算多因子得分（动量、技术、成交量、基本面、宏观、行业、CAPM_Beta）
3. 优化投资组合（最大化夏普比率）
4. 生成交易信号和权重分配

股票池：600519.SH 000858.SZ 603288.SH 600887.SH
市场基准：沪深300
时间段：2023-01-01 至 2023-12-31
```

---

## 完整示例

### 示例 1：CAPM 计算 + 多因子打分 + 投资组合优化（完整流程）

**目标**：完整的量化分析与投资组合优化流程

**步骤**：

1. **CAPM 计算**（计算 Beta 和预期收益率）
2. **多因子打分**（计算综合得分）
3. **投资组合优化**（基于预期收益率和协方差矩阵）
4. **生成交易信号**（基于综合得分和优化权重）

**代码**：

```python
from scripts.capm_core import calculate_beta_batch
from scripts.multi_factor_core import MultiFactorScorer
from scripts.optimize_portfolio import PortfolioOptimizer

# 1. CAPM 计算
betas = calculate_beta_batch(
    stocks=['600519.SH', '000858.SZ', '603288.SH', '600887.SH'],
    market_benchmark='000300.SH',
    start_date='2023-01-01',
    end_date='2023-12-31'
)

# 2. 多因子打分
scorer = MultiFactorScorer(
    factor_weights={
        'momentum': 0.20,
        'technical': 0.15,
        'volume': 0.10,
        'fundamental': 0.20,
        'macro': 0.10,
        'sector': 0.10,
        'capm_beta': 0.15
    }
)
scores = scorer.calculate_scores(betas)

# 3. 投资组合优化
optimizer = PortfolioOptimizer(
    expected_returns=betas['expected_return'],
    cov_matrix=betas['cov_matrix'],
    risk_free_rate=0.025
)
optimal_weights = optimizer.maximize_sharpe()

# 4. 生成交易信号
signals = generate_signals(scores, optimal_weights)
```

---

## 文件结构

```
capm-analysis/
├── SKILL.md                          # 本文档
├── app/
│   └── capm_app.py                 # Streamlit 交互式应用（扩展版）
├── scripts/
│   ├── capm_core.py               # CAPM 核心计算模块
│   ├── multi_factor_core.py       # 多因子打分核心模块（新增）
│   ├── optimize_portfolio.py      # 投资组合优化模块（新增）
│   ├── backtest.py                # 回测框架（新增）
│   └── generate_signals.py        # 交易信号生成（新增）
├── config/
│   └── factor_weights.yaml        # 因子权重配置（新增）
├── references/
│   ├── capm_theory.md           # CAPM 理论参考文档
│   └── multi_factor_guide.md    # 多因子打分指南（新增）
└── assets/
    └── example_screenshots/       # 应用截图（可选）
```

---

## 与现有 Skills 的关系

| Skill | 关系 | 集成方式 |
|-------|------|----------|
| `westock-data` | 数据源 | 调用 `westock-data` 获取 A股数据 |
| `efficient-frontier` | 已整合 | 投资组合优化功能已整合到本 skill |
| `auto-research-stock-selection` | 风险模型 | CAPM Beta 作为风险模型的一部分 |

---

## 限制与注意事项

1. **CAPM 假设限制**：见前文
2. **因子有效性**：多因子打分的效果取决于因子选择和数据质量
3. **过拟合风险**：避免在训练集上过度优化因子权重

---

## 默认表述

启动本 skill 时，向用户说明分析计划：

> 「我将基于 CAPM（资本资产定价模型）和多因子打分系统为您提供更完整的量化分析。
> 
> 分析步骤：
> 1. CAPM 计算（Beta、Alpha、预期收益率）
> 2. 多因子打分（动量、技术、成交量、基本面、宏观、行业、CAPM_Beta）
> 3. 投资组合优化（有效前沿、夏普比率最大化）
> 4. 生成交易信号和权重分配
> 
> 需要您提供：
> - 股票代码
> - 市场基准
> - 分析时间段
> - 因子权重偏好（可选）」

---

**版本历史**：
- v2.0（2026-06-27）：合并 multi-factor-scoring，增加多因子打分和投资组合优化功能
- v1.0（2026-06-25）：初始版本（仅 CAPM 计算）
