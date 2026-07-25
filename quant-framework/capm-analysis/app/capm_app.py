"""
CAPM 分析交互式 Web 应用

使用 Streamlit 构建，支持：
- 侧边栏配置（市场、基准、股票、时间段等）
- 主界面展示（表格、散点图、SML、模型诊断）
- A股/美股/港股适配
"""

import sys
import json
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# 导入 CAPM 核心计算模块
sys.path.insert(0, '../scripts')
from capm_core import (
    get_risk_free_rate,
    get_market_data,
    get_stock_data,
    calculate_returns,
    calculate_beta,
    calculate_expected_return,
    run_capm_analysis
)


# 页面配置
st.set_page_config(
    page_title="CAPM 分析工具",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 标题
st.title("📊 CAPM 分析工具")
st.markdown("---")

# 侧边栏配置
st.sidebar.header("⚙️ 配置")

# 1. 选择市场
market = st.sidebar.selectbox(
    "选择市场",
    options=['CN', 'US', 'HK'],
    format_func=lambda x: {'CN': '中国 A股', 'US': '美国美股', 'HK': '香港港股'}[x],
    index=0
)

# 2. 选择市场基准
benchmark_options = {
    'CN': ['000300.SH', '000905.SH', '000852.SH'],
    'US': ['^GSPC', '^DJI', '^IXIC'],
    'HK': ['^HSI', '^HSCE']
}
benchmark = st.sidebar.selectbox(
    "选择市场基准",
    options=benchmark_options[market],
    format_func=lambda x: {
        '000300.SH': '沪深300',
        '000905.SH': '中证500',
        '000852.SH': '中证1000',
        '^GSPC': 'S&P 500',
        '^DJI': '道琼斯指数',
        '^IXIC': '纳斯达克指数',
        '^HSI': '恒生指数',
        '^HSCE': '恒生中国企业指数'
    }[x]
)

# 3. 输入股票代码
stocks_input = st.sidebar.text_area(
    "输入股票代码（每行一只）",
    value="600519.SH\n000858.SZ\n603288.SH",
    height=100
)
stocks = [s.strip() for s in stocks_input.split('\n') if s.strip()]

# 4. 选择时间段
col1, col2 = st.sidebar.columns(2)
with col1:
    start_date = st.date_input(
        "开始日期",
        value=datetime(2023, 1, 1)
    )
with col2:
    end_date = st.date_input(
        "结束日期",
        value=datetime(2023, 12, 31)
    )

# 5. 选择数据频率
frequency = st.sidebar.selectbox(
    "数据频率",
    options=['daily', 'weekly', 'monthly'],
    format_func=lambda x: {'daily': '日度', 'weekly': '周度', 'monthly': '月度'}[x]
)

# 6. 选择无风险利率期限
risk_free_tenor = st.sidebar.selectbox(
    "无风险利率期限",
    options=['10Y', '1Y', '3M', '1M'],
    format_func=lambda x: {'10Y': '10年期', '1Y': '1年期', '3M': '3个月', '1M': '1个月'}[x]
)

# 7. 运行分析按钮
run_analysis = st.sidebar.button("🚀 运行分析", type="primary")

# 主界面
if run_analysis:
    if not stocks:
        st.error("请至少输入一只股票代码！")
        st.stop()
    
    # 创建进度条
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # 存储所有股票的分析结果
    all_results = []
    
    # 遍历每只股票
    for i, stock in enumerate(stocks):
        status_text.text(f"正在分析 {stock}（{i+1}/{len(stocks)}）...")
        
        try:
            # 运行 CAPM 分析
            result = run_capm_analysis(
                stock=stock,
                benchmark=benchmark,
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d'),
                risk_free_tenor=risk_free_tenor,
                frequency=frequency,
                use_westock=False  # 暂时不使用 westock-data
            )
            all_results.append(result)
        except Exception as e:
            st.warning(f"分析 {stock} 失败：{e}")
            continue
        
        # 更新进度条
        progress_bar.progress((i + 1) / len(stocks))
    
    status_text.text("分析完成！")
    
    if not all_results:
        st.error("所有股票分析均失败，请检查输入或数据源！")
        st.stop()
    
    # 转换为 DataFrame
    results_df = pd.DataFrame(all_results)
    
    # ========== 展示结果 ==========
    
    # 1. 结果表格
    st.header("📋 CAPM 分析结果")
    
    display_df = results_df[[
        'stock', 'beta', 'alpha', 'r_squared', 'p_value', 'expected_return'
    ]].copy()
    display_df.columns = ['股票', 'Beta', 'Alpha（年化）', 'R²', 'p 值', '预期收益率（CAPM）']
    display_df['Beta'] = display_df['Beta'].round(4)
    display_df['Alpha（年化）'] = (display_df['Alpha（年化）'] * 100).round(2).astype(str) + '%'
    display_df['R²'] = display_df['R²'].round(4)
    display_df['p 值'] = display_df['p 值'].round(4)
    display_df['预期收益率（CAPM）'] = (display_df['预期收益率（CAPM）'] * 100).round(2).astype(str) + '%'
    
    st.dataframe(display_df, use_container_width=True)
    
    st.markdown("---")
    
    # 2. 散点图（个股收益率 vs 市场收益率）
    st.header("📈 散点图：个股收益率 vs 市场收益率")
    
    # 选择要展示的股票
    selected_stock = st.selectbox(
        "选择要展示的股票",
        options=stocks,
        index=0
    )
    
    # 获取该股票的数据
    selected_result = [r for r in all_results if r['stock'] == selected_stock][0]
    
    # 重新获取收益率数据（用于绘图）
    risk_free_rate = results_df[results_df['stock'] == selected_stock]['risk_free_rate'].values[0]
    market_returns = calculate_returns(get_market_data(
        benchmark,
        start_date.strftime('%Y-%m-%d'),
        end_date.strftime('%Y-%m-%d'),
        frequency
    ))
    stock_returns = calculate_returns(get_stock_data(
        selected_stock,
        start_date.strftime('%Y-%m-%d'),
        end_date.strftime('%Y-%m-%d'),
        frequency
    ))
    
    # 对齐数据
    df_plot = pd.DataFrame({
        'market_return': market_returns.iloc[:, 0],
        'stock_return': stock_returns.iloc[:, 0]
    }).dropna()
    
    # 计算回归线
    beta = selected_result['beta']
    alpha = selected_result['alpha'] / 252  # 转换为日度
    x_line = np.linspace(df_plot['market_return'].min(), df_plot['market_return'].max(), 100)
    y_line = alpha + beta * x_line
    
    # 绘制散点图
    fig_scatter = go.Figure()
    
    # 散点
    fig_scatter.add_trace(go.Scatter(
        x=df_plot['market_return'],
        y=df_plot['stock_return'],
        mode='markers',
        name='观测值',
        marker=dict(size=8, opacity=0.6)
    ))
    
    # 回归线
    fig_scatter.add_trace(go.Scatter(
        x=x_line,
        y=y_line,
        mode='lines',
        name=f'回归线（Beta = {beta:.4f}）',
        line=dict(color='red', width=2)
    ))
    
    fig_scatter.update_layout(
        title=f'{selected_stock}：个股收益率 vs 市场收益率',
        xaxis_title='市场收益率',
        yaxis_title='个股收益率',
        showlegend=True,
        width=800,
        height=500
    )
    
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    st.markdown("---")
    
    # 3. SML（证券市场线）
    st.header("📉 SML（证券市场线）")
    
    # 计算所有股票的风险溢价和超额收益率
    sml_data = []
    for result in all_results:
        sml_data.append({
            'stock': result['stock'],
            'beta': result['beta'],
            'excess_return': result['expected_return'] - result['risk_free_rate']
        })
    
    sml_df = pd.DataFrame(sml_data)
    
    # 计算 SML 线
    market_excess_return = results_df['market_excess_return'].mean()
    x_sml = np.linspace(0, sml_df['beta'].max() * 1.2, 100)
    y_sml = results_df['risk_free_rate'].mean() + x_sml * market_excess_return
    
    # 绘制 SML
    fig_sml = go.Figure()
    
    # SML 线
    fig_sml.add_trace(go.Scatter(
        x=x_sml,
        y=y_sml,
        mode='lines',
        name='SML（证券市场线）',
        line=dict(color='blue', width=2)
    ))
    
    # 个股散点
    fig_sml.add_trace(go.Scatter(
        x=sml_df['beta'],
        y=sml_df['excess_return'],
        mode='markers+text',
        name='个股',
        marker=dict(size=10, opacity=0.7),
        text=sml_df['stock'],
        textposition='top center'
    ))
    
    fig_sml.update_layout(
        title='证券市场线（SML）',
        xaxis_title='Beta（β）',
        yaxis_title='预期收益率',
        showlegend=True,
        width=800,
        height=500
    )
    
    st.plotly_chart(fig_sml, use_container_width=True)
    
    st.markdown("---")
    
    # 4. 模型诊断
    st.header("🔍 模型诊断")
    
    # 选择要诊断的股票
    diagnose_stock = st.selectbox(
        "选择要诊断的股票",
        options=stocks,
        index=0,
        key='diagnose_stock'
    )
    
    # 获取该股票的回归结果
    diagnose_result = [r for r in all_results if r['stock'] == diagnose_stock][0]
    
    # 重新运行回归（获取残差）
    risk_free_rate = diagnose_result['risk_free_rate']
    market_returns = calculate_returns(get_market_data(
        benchmark,
        start_date.strftime('%Y-%m-%d'),
        end_date.strftime('%Y-%m-%d'),
        frequency
    ))
    stock_returns = calculate_returns(get_stock_data(
        diagnose_stock,
        start_date.strftime('%Y-%m-%d'),
        end_date.strftime('%Y-%m-%d'),
        frequency
    ))
    
    beta_result = calculate_beta(
        stock_returns.iloc[:, 0],
        market_returns.iloc[:, 0],
        risk_free_rate
    )
    
    # 残差分析
    if 'residuals' in beta_result:
        residuals = np.array(beta_result['residuals'])
        fitted_values = np.array(beta_result['fitted_values'])
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 残差散点图
            fig_residual = go.Figure()
            fig_residual.add_trace(go.Scatter(
                x=fitted_values,
                y=residuals,
                mode='markers',
                marker=dict(size=8, opacity=0.6)
            ))
            fig_residual.add_hline(y=0, line_dash='dash', line_color='red')
            fig_residual.update_layout(
                title='残差 vs 拟合值',
                xaxis_title='拟合值',
                yaxis_title='残差',
                width=400,
                height=400
            )
            st.plotly_chart(fig_residual, use_container_width=True)
        
        with col2:
            # 残差 QQ 图
            from scipy import stats
            fig_qq = go.Figure()
            theoretical_quantiles = np.sort(np.random.normal(0, 1, len(residuals)))
            sorted_residuals = np.sort((residuals - np.mean(residuals)) / np.std(residuals))
            
            fig_qq.add_trace(go.Scatter(
                x=theoretical_quantiles,
                y=sorted_residuals,
                mode='markers',
                marker=dict(size=8, opacity=0.6)
            ))
            
            # 参考线（y = x）
            min_val = min(theoretical_quantiles.min(), sorted_residuals.min())
            max_val = max(theoretical_quantiles.max(), sorted_residuals.max())
            fig_qq.add_trace(go.Scatter(
                x=[min_val, max_val],
                y=[min_val, max_val],
                mode='lines',
                line=dict(color='red', dash='dash'),
                name='参考线（y = x）'
            ))
            
            fig_qq.update_layout(
                title='残差 QQ 图（检验正态性）',
                xaxis_title='理论分位数',
                yaxis_title='样本分位数',
                showlegend=True,
                width=400,
                height=400
            )
            st.plotly_chart(fig_qq, use_container_width=True)
        
        # 模型诊断结论
        st.subheader("诊断结论")
        
        # 1. 异方差性检验（残差 vs 拟合值）
        # 简单判断：残差是否随拟合值变化
        residual_trend = np.corrcoef(fitted_values, np.abs(residuals))[0, 1]
        if abs(residual_trend) > 0.3:
            st.warning("⚠️ 可能存在异方差性（残差随拟合值变化）")
        else:
            st.success("✅ 残差分布较均匀（无异方差性）")
        
        # 2. 正态性检验（QQ 图）
        # 简单判断：点是否近似落在参考线上
        qq_deviation = np.mean(np.abs(sorted_residuals - theoretical_quantiles))
        if qq_deviation > 0.5:
            st.warning("⚠️ 残差可能不服从正态分布")
        else:
            st.success("✅ 残差近似服从正态分布")
        
        # 3. 显著性检验（p 值）
        p_value = beta_result['p_value']
        if p_value < 0.05:
            st.success(f"✅ Beta 系数显著不为 0（p = {p_value:.4f} < 0.05）")
        else:
            st.warning(f"⚠️ Beta 系数可能不显著（p = {p_value:.4f} >= 0.05）")
    
    else:
        st.info("模型诊断需要 OLS 回归结果（请安装 statsmodels）")
    
    st.markdown("---")
    
    # 5. 导出结果
    st.header("💾 导出结果")
    
    if st.button("导出为 JSON"):
        json_str = json.dumps(all_results, indent=2, ensure_ascii=False)
        st.download_button(
            label="下载 JSON 文件",
            data=json_str,
            file_name=f"capm_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

else:
    # 默认展示说明
    st.info("""
    👈 请在左侧边栏配置参数，然后点击"运行分析"按钮。
    
    **功能说明**：
    1. **CAPM 计算**：计算 Beta、Alpha、R²、预期收益率
    2. **散点图**：展示个股收益率 vs 市场收益率
    3. **SML（证券市场线）**：展示所有股票的风险-收益关系
    4. **模型诊断**：残差分析、QQ 图、显著性检验
    
    **数据来源**：
    - A股：akshare（需要安装：`pip install akshare`）
    - 美股/港股：yfinance（需要安装：`pip install yfinance`）
    """)
    
    st.markdown("---")
    
    st.subheader("📚 CAPM 理论简介")
    st.markdown("""
    **CAPM（资本资产定价模型）** 是由 William Sharpe（1964）提出的金融资产定价模型。
    
    核心公式：
    ```
    E(R_i) = R_f + β × (E(R_m) - R_f)
    ```
    
    其中：
    - `E(R_i)`：股票 i 的预期收益率
    - `R_f`：无风险利率
    - `β`：贝塔系数（系统风险敞口）
    - `E(R_m)`：市场组合的预期收益率
    
    **解释**：
    - **Beta > 1**：股票波动性大于市场（如科技股）
    - **Beta < 1**：股票波动性小于市场（如公用事业股）
    - **Beta = 1**：股票波动性等于市场（如指数基金）
    
    **模型假设**：
    1. 投资者理性、风险厌恶
    2. 无交易成本、无税收
    3. 所有投资者对预期收益率和风险的判断一致
    4. 可以无限制借贷无风险资产
    """)

# 页脚
st.markdown("---")
st.markdown("CAPM 分析工具 | 基于现代投资组合理论（MPT） | 修复版")
