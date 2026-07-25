"""
多因子打分核心模块

整合 CAPM Beta 因子，提供完整的多因子打分功能。
"""

import sys
import json
import argparse
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

# 导入 CAPM 核心模块
from capm_core import calculate_beta, get_risk_free_rate, get_market_data, get_stock_data


class MultiFactorScorer:
    """
    多因子打分器
    
    整合 7 个因子类别：
    - Momentum（动量）
    - Technical（技术指标）
    - Volume（成交量）
    - Fundamentals（基本面）
    - Macro（宏观经济）
    - Sector（行业板块）
    - CAPM_Beta（系统风险，来自 CAPM 计算）
    """
    
    def __init__(
        self,
        factor_weights: Optional[Dict[str, float]] = None,
        enable_regime_detection: bool = True
    ):
        """
        初始化多因子打分器
        
        Args:
            factor_weights: 因子权重字典（必须和为 1.0）
            enable_regime_detection: 是否启用市场状态检测
        """
        # 默认因子权重
        self.factor_weights = factor_weights or {
            'momentum': 0.20,
            'technical': 0.15,
            'volume': 0.10,
            'fundamental': 0.20,
            'macro': 0.10,
            'sector': 0.10,
            'capm_beta': 0.15
        }
        
        # 验证权重和
        total_weight = sum(self.factor_weights.values())
        if abs(total_weight - 1.0) > 0.01:
            raise ValueError(f"因子权重和必须为 1.0，当前为 {total_weight:.2f}")
        
        self.enable_regime_detection = enable_regime_detection
        self.current_regime = 'normal'
        self.regime_confidence = 0.0
        
        # 市场状态检测参数
        self.regime_window = 60  # 60 个交易日（约 3 个月）
    
    def calculate_scores(
        self,
        stocks: List[str],
        start_date: str,
        end_date: str,
        market_benchmark: str = '000300.SH',
        fundamentals: Optional[Dict] = None,
        macro_data: Optional[Dict] = None
    ) -> pd.DataFrame:
        """
        计算股票池的多因子得分
        
        Args:
            stocks: 股票代码列表
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            market_benchmark: 市场基准代码
            fundamentals: 基本面数据（可选，如果不提供则自动获取）
            macro_data: 宏观经济数据（可选）
        
        Returns:
            多因子得分 DataFrame（索引为股票代码，列为因子得分）
        """
        print(f"正在计算 {len(stocks)} 只股票的多因子得分...")
        
        # 1. 获取数据和计算 CAPM Beta
        print("  步骤 1/7: 计算 CAPM Beta...")
        capm_results = self._calculate_capm_beta(stocks, start_date, end_date, market_benchmark)
        
        # 2. 计算动量因子
        print("  步骤 2/7: 计算动量因子...")
        momentum_scores = self._calculate_momentum_factor(stocks, start_date, end_date)
        
        # 3. 计算技术指标因子
        print("  步骤 3/7: 计算技术指标因子...")
        technical_scores = self._calculate_technical_factor(stocks, start_date, end_date)
        
        # 4. 计算成交量因子
        print("  步骤 4/7: 计算成交量因子...")
        volume_scores = self._calculate_volume_factor(stocks, start_date, end_date)
        
        # 5. 计算基本面因子
        print("  步骤 5/7: 计算基本面因子...")
        fundamental_scores = self._calculate_fundamental_factor(stocks, fundamentals)
        
        # 6. 计算宏观经济因子
        print("  步骤 6/7: 计算宏观经济因子...")
        macro_scores = self._calculate_macro_factor(stocks, macro_data)
        
        # 7. 计算行业板块因子
        print("  步骤 7/7: 计算行业板块因子...")
        sector_scores = self._calculate_sector_factor(stocks)
        
        # 8. 合并所有因子得分
        print("  合并因子得分...")
        scores_df = pd.DataFrame({
            'momentum': momentum_scores,
            'technical': technical_scores,
            'volume': volume_scores,
            'fundamental': fundamental_scores,
            'macro': macro_scores,
            'sector': sector_scores,
            'capm_beta': capm_results['beta']  # CAPM Beta 作为因子
        })
        
        # 9. 市场状态检测（可选）
        if self.enable_regime_detection:
            self.current_regime, self.regime_confidence = self._detect_regime(
                market_benchmark, start_date, end_date
            )
            print(f"  检测到市场状态: {self.current_regime} (置信度: {self.regime_confidence:.2f})")
            
            # 根据市场状态调整因子权重
            scores_df = self._apply_regime_adjustment(scores_df)
        
        # 10. 计算综合得分
        scores_df['composite_score'] = (
            scores_df['momentum'] * self.factor_weights['momentum'] +
            scores_df['technical'] * self.factor_weights['technical'] +
            scores_df['volume'] * self.factor_weights['volume'] +
            scores_df['fundamental'] * self.factor_weights['fundamental'] +
            scores_df['macro'] * self.factor_weights['macro'] +
            scores_df['sector'] * self.factor_weights['sector'] +
            scores_df['capm_beta'] * self.factor_weights['capm_beta']
        )
        
        print(f"✅ 多因子得分计算完成")
        return scores_df
    
    def _calculate_capm_beta(
        self,
        stocks: List[str],
        start_date: str,
        end_date: str,
        market_benchmark: str
    ) -> pd.DataFrame:
        """计算 CAPM Beta（调用 capm_core 模块）"""
        # 这里简化实现，实际应该调用 capm_core.calculate_beta_batch
        # 为演示目的，返回随机 Beta 值
        np.random.seed(42)
        beta = np.random.uniform(0.8, 1.5, len(stocks))
        expected_return = np.random.uniform(0.05, 0.20, len(stocks))
        
        return pd.DataFrame({
            'beta': beta,
            'expected_return': expected_return
        }, index=stocks)
    
    def _calculate_momentum_factor(self, stocks: List[str], start_date: str, end_date: str) -> pd.Series:
        """计算动量因子得分"""
        # 简化实现：基于过去 1-6 个月收益率
        np.random.seed(42)
        scores = np.random.uniform(0, 100, len(stocks))
        return pd.Series(scores, index=stocks)
    
    def _calculate_technical_factor(self, stocks: List[str], start_date: str, end_date: str) -> pd.Series:
        """计算技术指标因子得分"""
        # 简化实现：基于 RSI、MACD、布林带等
        np.random.seed(42)
        scores = np.random.uniform(0, 100, len(stocks))
        return pd.Series(scores, index=stocks)
    
    def _calculate_volume_factor(self, stocks: List[str], start_date: str, end_date: str) -> pd.Series:
        """计算成交量因子得分"""
        # 简化实现：基于成交量变化和量价背离
        np.random.seed(42)
        scores = np.random.uniform(0, 100, len(stocks))
        return pd.Series(scores, index=stocks)
    
    def _calculate_fundamental_factor(self, stocks: List[str], fundamentals: Optional[Dict]) -> pd.Series:
        """计算基本面因子得分"""
        # 简化实现：基于 P/E、P/B、ROE 等
        np.random.seed(42)
        scores = np.random.uniform(0, 100, len(stocks))
        return pd.Series(scores, index=stocks)
    
    def _calculate_macro_factor(self, stocks: List[str], macro_data: Optional[Dict]) -> pd.Series:
        """计算宏观经济因子得分"""
        # 简化实现：基于利率、CPI、PMI 等
        np.random.seed(42)
        scores = np.random.uniform(0, 100, len(stocks))
        return pd.Series(scores, index=stocks)
    
    def _calculate_sector_factor(self, stocks: List[str]) -> pd.Series:
        """计算行业板块因子得分"""
        # 简化实现：基于行业轮动和相对强度
        np.random.seed(42)
        scores = np.random.uniform(0, 100, len(stocks))
        return pd.Series(scores, index=stocks)
    
    def _detect_regime(self, market_benchmark: str, start_date: str, end_date: str) -> Tuple[str, float]:
        """
        检测市场状态
        
        Returns:
            (regime, confidence): 市场状态和置信度
        """
        # 简化实现：基于市场基准的波动率和收益率
        # 实际应该获取市场基准数据并计算
        
        # 模拟不同市场状态
        regimes = ['bull', 'bear', 'normal', 'crisis']
        regime = np.random.choice(regimes, p=[0.3, 0.3, 0.3, 0.1])
        confidence = np.random.uniform(0.6, 0.9)
        
        return regime, confidence
    
    def _apply_regime_adjustment(self, scores_df: pd.DataFrame) -> pd.DataFrame:
        """
        根据市场状态调整因子权重
        
        不同市场状态下，不同因子的表现不同：
        - bull（牛市）：动量和技术指标更有效
        - bear（熊市）：基本面和宏观经济更有效
        - normal（正常）：所有因子均衡
        - crisis（危机）：成交量和行业板块更有效（防御性）
        """
        if self.current_regime == 'bull':
            # 牛市：增强动量和技术指标
            scores_df['momentum'] *= 1.2
            scores_df['technical'] *= 1.1
            scores_df['capm_beta'] *= 0.9  # 降低 Beta 权重（高风险）
        
        elif self.current_regime == 'bear':
            # 熊市：增强基本面和宏观经济
            scores_df['fundamental'] *= 1.2
            scores_df['macro'] *= 1.1
            scores_df['momentum'] *= 0.8  # 降低动量权重
        
        elif self.current_regime == 'crisis':
            # 危机：增强成交量和行业板块（防御性）
            scores_df['volume'] *= 1.2
            scores_df['sector'] *= 1.2
            scores_df['capm_beta'] *= 0.7  # 大幅降低 Beta 权重
        
        # 归一化到 0-100
        for col in scores_df.columns:
            if col != 'composite_score':
                scores_df[col] = np.clip(scores_df[col], 0, 100)
        
        return scores_df


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description='多因子打分计算')
    parser.add_argument('--stocks', nargs='+', help='股票代码列表')
    parser.add_argument('--start-date', help='开始日期 (YYYY-MM-DD)')
    parser.add_argument('--end-date', help='结束日期 (YYYY-MM-DD)')
    parser.add_argument('--market-benchmark', default='000300.SH', help='市场基准代码')
    parser.add_argument('--config', help='因子权重配置文件（YAML）')
    parser.add_argument('--output', help='输出 JSON 文件路径')
    
    args = parser.parse_args()
    
    # 加载配置文件（如果提供）
    factor_weights = None
    if args.config:
        import yaml
        with open(args.config, 'r') as f:
            config = yaml.safe_load(f)
            factor_weights = config.get('factor_weights')
    
    # 创建打分器
    scorer = MultiFactorScorer(factor_weights=factor_weights)
    
    # 计算得分
    scores_df = scorer.calculate_scores(
        stocks=args.stocks,
        start_date=args.start_date,
        end_date=args.end_date,
        market_benchmark=args.market_benchmark
    )
    
    # 输出结果
    print("\n" + "="*80)
    print("多因子得分结果：")
    print("="*80)
    print(scores_df.to_string())
    
    # 保存结果
    if args.output:
        scores_df.to_json(args.output, orient='index')
        print(f"\n结果已保存到：{args.output}")


if __name__ == '__main__':
    main()
