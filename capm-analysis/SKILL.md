---
name: capm-analysis
description: >
  CAPM（资本资产定价模型）分析与可视化工具，支持A股/美股/港股适配、
  量化框架集成、交互式Web应用。修复了原仓库的Beta计算不准确、
  无风险利率固定、市场基准单一、缺少模型诊断等缺陷。
  触发场景：用户提到「CAPM」、「贝塔系数」、「预期收益率」、
  「系统风险」、「市场基准」、「量化因子」等。
agent_created: true
---

# CAPM Analysis — CAPM 分析与量化集成

A股适配 + 量化框架集成版的 CAPM 分析工具，支持交互式 Web 应用和量化框架集成。

---

## 核心功能

### 1. CAPM 计算（修复版）

**修复的缺陷**：

| 原仓库缺陷 | 修复方案 | 状态 |
|------------|----------|------|
| Beta 计算不准确（`np.polyfit`） | 使用 `statsmodels.OLS` 进行稳健线性回归 | ✅ |
| 无风险利率固定（4.5%） | 自动获取当前无风险利率（10年期国债收益率） | ✅ |
| 市场基准单一（仅 S&P 500） | 支持多市场基准（沪深300、中证500、恒生指数、S&P 500） | ✅ |
| 缺少模型诊断 | 增加 R²、残差分析、显著性检验 | ✅ |

**计算步骤**：

1. **获取无风险利率**（`get_risk_free_rate()`）
   - 中国市场：10年期国债收益率（来自 `westock-data` 或 `akshare`）
   - 美国市场：10年期国债收益率（来自 FRED API）
   - 默认值：中国 2.5%、美国 4.5%

2. **获取市场基准数据**（`get_market_data()`）
   - 支持基准：
     - `000300.SH`（沪深300）
     - `000905.SH`（中证500）
     - `HSI`（恒生指数）
     - `^GSPC`（S&P 500）
   - 数据频率：日度 / 周度 / 月度（可配置）

3. **计算 Beta 系数**（`calculate_beta()`）
   - 使用 `statsmodels.OLS` 进行线性回归：
     ```
     R_i - R_f = α + β × (R_m - R_f) + ε
     ```
   - 输出：
     - `beta`：贝塔系数（系统风险敞口）
     - `alpha`：阿尔法（超额收益）
     - `r_squared`：拟合优度
     - `p_value`：Beta 显著性检验 p 值
     - `std_error`：Beta 标准误

4. **计算预期收益率**（`calculate_expected_return()`）
   - CAPM 公式：
     ```
     E(R_i) = R_f + β × (E(R_m) - R_f)
     ```
   - 其中：
     - `E(R_i)`：股票 i 的预期收益率
     - `R_f`：无风险利率
     - `β`：贝塔系数
     - `E(R_m)`：市场组合的预期收益率

---

### 2. A股适配

**市场基准**：
- 默认：沪深300（`000300.SH`）
- 可选：中证500（`000905.SH`）、中证1000（`000852.SH`）

**无风险利率**：
- 默认：10年期国债收益率（来自 `westock-data`）
- 备选：1个月、3个月、1年期国债收益率

**数据源**：
- 优先：`westock-data` skill（已针对 A股优化）
- 备选：`akshare` 库（需要安装：`pip install akshare`）

**涨跌停处理**：
- 计算收益率时，自动剔除涨跌停日的异常值
- 可选：使用复权价格（前复权 / 后复权）

---

### 3. 量化框架集成

**与 `multi-factor-scoring` skill 集成**：

CAPM 的 Beta 系数可以作为**风险因子**集成到多因子打分系统：

```
多因子打分 = w1 × Value因子 + w2 × Momentum因子 + w3 × Beta因子 + ...
```

**集成步骤**：

1. **计算个股 Beta**（`scripts/calculate_beta_batch.py`）
   - 输入：股票池（如沪深300成分股）
   - 输出：Beta 系数矩阵（DataFrame）

2. **Beta 因子化处理**（`scripts/process_beta_factor.py`）
   - Beta 越高 = 系统风险越大 = 预期收益率越高（CAPM 理论）
   - 但高 Beta 也可能意味着高风险，需要结合其他因子

3. **集成到多因子打分**（`multi-factor-scoring` skill）
   - 在 `factors/` 目录下新增 `beta_factor.py`
   - 将 Beta 因子纳入因子库

**与 `efficient-frontier` skill 集成**：

CAPM 的预期收益率可以作为**输入**用于投资组合优化：

```
预期收益率（CAPM）= 无风险利率 + Beta × 市场风险溢价
```

---

### 4. 交互式 Web 应用

**技术栈**：Streamlit

**功能**：

1. **侧边栏配置**：
   - 选择市场（A股 / 美股 / 港股）
   - 选择市场基准（沪深300 / 中证500 / S&P 500 / ...）
   - 输入股票代码（支持多只）
   - 选择时间段
   - 选择数据频率（日度 / 周度 / 月度）
   - 选择无风险利率期限（10年 / 1年 / 3个月 / 1个月）

2. **主界面展示**：
   - **表格**：Beta、Alpha、R²、预期收益率、p 值
   - **散点图**：个股收益率 vs 市场收益率（附带回归线）
   - **残差图**：检验线性回归假设
   - **SML（证券市场线）**：展示所有股票的风险-收益关系

3. **模型诊断**：
   - 残差 QQ 图（检验正态性）
   - 残差 vs 拟合值图（检验同方差性）
   - 高杠杆点检测（识别异常值）

---

## 安装依赖

```bash
# 核心依赖
pip install pandas numpy statsmodels yfinance pandas-datareader streamlit plotly

# A股数据源（可选）
pip install akshare

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
# 计算单只股票的 CAPM
python scripts/calculate_capm.py \
  --stock 600519.SH \
  --market-benchmark 000300.SH \
  --start-date 2023-01-01 \
  --end-date 2023-12-31 \
  --risk-free-tenor 10Y

# 批量计算股票池的 Beta
python scripts/calculate_beta_batch.py \
  --stocks 600519.SH 000858.SZ 603288.SH \
  --market-benchmark 000300.SH \
  --output beta_results.json
```

---

### 方式三：在 WorkBuddy 中调用

```
@skill:capm-analysis

分析以下股票的 CAPM：
- 股票池：600519.SH（茅台）、000858.SZ（五粮液）、
          603288.SH（海天味业）、600887.SH（伊利股份）
- 市场基准：沪深300（000300.SH）
- 时间段：2023-01-01 至 2023-12-31
- 无风险利率：10年期国债收益率

输出：
1. 每只股票的 Beta、Alpha、R²、预期收益率
2. 散点图（个股收益率 vs 市场收益率）
3. SML（证券市场线）
4. 模型诊断结果
```

---

## 完整示例

### 示例 1：A股消费板块 CAPM 分析

**目标**：分析消费板块龙头股票的系统性风险敞口

**步骤**：

1. **获取数据**（使用 `westock-data`）：
   ```
   @skill:westock-data 获取股票日度价格数据
   股票代码：600519.SH 000858.SZ 603288.SH 600887.SH 000568.SZ
   开始日期：2023-01-01
   结束日期：2023-12-31
   字段：close（收盘价）
   频率：daily
   复权：前复权（qfq）
   ```

2. **获取市场基准数据**：
   ```
   @skill:westock-data 获取指数日度数据
   指数代码：000300.SH
   开始日期：2023-01-01
   结束日期：2023-12-31
   字段：close（收盘价）
   ```

3. **获取无风险利率**：
   ```
   @skill:westock-data 获取国债收益率
   期限：10年期
   日期：2023-12-31
   ```

4. **运行 CAPM 分析**：
   ```bash
   streamlit run app/capm_app.py
   ```
   - 在侧边栏输入股票代码
   - 选择市场基准：沪深300
   - 选择时间段：2023-01-01 至 2023-12-31
   - 点击"运行分析"

5. **解读结果**：
   - **Beta > 1**：股票波动性大于市场（如茅台 Beta ≈ 1.2）
   - **Beta < 1**：股票波动性小于市场（如伊利 Beta ≈ 0.8）
   - **R² 高**：CAPM 模型解释力度强
   - **R² 低**：可能存在其他未被捕捉的风险因子

---

### 示例 2：集成到多因子打分系统

**目标**：将 Beta 因子纳入多因子打分系统

**步骤**：

1. **计算股票池的 Beta**（`scripts/calculate_beta_batch.py`）

2. **Beta 因子化**（`scripts/process_beta_factor.py`）：
   - 对 Beta 进行标准化（z-score）
   - 根据 CAPM 理论，高 Beta 应该对应高预期收益率
   - 因此，Beta 因子得分 = Beta 值（越高越好）

3. **集成到 `multi-factor-scoring`**：
   - 在 `factors/` 目录下新增 `beta_factor.py`
   - 修改 `config/factor_weights.yaml`，增加 Beta 因子权重

---

## 文件结构

```
capm-analysis/
├── SKILL.md                          # 本文档
├── app/
│   └── capm_app.py                 # Streamlit 交互式应用
├── scripts/
│   ├── capm_core.py               # CAPM 核心计算模块
│   ├── calculate_capm.py          # 单只股票 CAPM 计算脚本
│   ├── calculate_beta_batch.py   # 批量计算 Beta 脚本
│   └── process_beta_factor.py    # Beta 因子化处理脚本
├── references/
│   └── capm_theory.md           # CAPM 理论参考文档
└── assets/
    └── example_screenshots/       # 应用截图（可选）
```

---

## 与现有 Skills 的关系

| Skill | 关系 | 集成方式 |
|-------|------|----------|
| `westock-data` | 数据源 | 调用 `westock-data` 获取 A股数据 |
| `multi-factor-scoring` | 因子提供 | 将 Beta 作为风险因子集成 |
| `efficient-frontier` | 输入提供 | CAPM 预期收益率作为优化输入 |
| `auto-research-stock-selection` | 风险模型 | CAPM Beta 作为风险模型的一部分 |

---

## 限制与注意事项

1. **CAPM 假设限制**：
   - 假设投资者理性、风险厌恶
   - 假设无交易成本、无税收
   - 假设所有投资者对预期收益率和风险的判断一致
   - 现实中这些假设可能不成立

2. **Beta 不稳定性**：
   - Beta 可能随时间变化（结构性断裂）
   - 建议使用滚动窗口计算 Beta（如过去 1年、2年、3年）

3. **市场基准选择**：
   - 不同市场基准会导致不同的 Beta 估计
   - 建议尝试多个市场基准，选择 R² 最高的

---

## 默认表述

启动本 skill 时，向用户说明分析计划：

> 「我将基于 CAPM（资本资产定价模型）为您分析股票的系统风险。
> 
> 分析步骤：
> 1. 获取股票收益率数据（使用 westock-data 或 akshare）
> 2. 获取市场基准收益率（沪深300 / 中证500 / ...）
> 3. 获取无风险利率（10年期国债收益率）
> 4. 计算 Beta 系数、Alpha、R²、预期收益率
> 5. 绘制散点图和 SML（证券市场线）
> 6. 进行模型诊断（残差分析、显著性检验）
> 
> 需要您提供：
> - 股票代码（如：600519.SH）
> - 市场基准（默认：沪深300）
> - 分析时间段
> - 是否集成到多因子打分系统」
