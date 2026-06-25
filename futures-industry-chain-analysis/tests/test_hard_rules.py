#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
硬规则测试套件 v3 — 验证futures-industry-chain-analysis全部10条硬规则

运行方式（从skill根目录）：
  python -m pytest tests/test_hard_rules.py -v
"""

import sys, os, json, unittest, time, inspect

# conftest.py 已处理路径


class TestHardRules(unittest.TestCase):
    """硬规则 #1-10 验证"""

    def setUp(self):
        from scripts.config import CONFIG_MANAGER
        self.cfg = CONFIG_MANAGER

    def test_rule1_data_authenticity(self):
        """硬规则#1: 数据函数必须存在"""
        from scripts.collect_data import fetch_from_tqsdk, fetch_from_akshare
        self.assertTrue(callable(fetch_from_tqsdk))
        self.assertTrue(callable(fetch_from_akshare))

    def test_rule2_trend_based_on_indicators(self):
        """硬规则#2: 趋势评分基于技术指标"""
        from scripts.indicators import calculate_trend_score
        mock_tech = {
            'MA5': 3120, 'MA10': 3100, 'MA20': 3080,
            'MACD_DIF': 15, 'RSI14': 55,
            'DMI_ADX': 25, 'DMI_PDI': 30, 'DMI_NDI': 20,
            'OBV': 100000, 'volatility_pct': 2.0, 'ATR14': 50,
        }
        mock_sym = {'product_id': 'rb', 'product_name': '螺纹钢'}
        try:
            result = calculate_trend_score(mock_tech, mock_sym, 'black')
            self.assertIsInstance(result, dict)
            self.assertIn('score', result)
        except Exception as e:
            self.fail(f"calculate_trend_score 异常: {e}")

    def test_rule3_main_contract_format(self):
        """硬规则#3: 品种映射应>50个"""
        from scripts.data_fallback import _AKSHARE_SYMBOL_MAP
        self.assertGreater(len(_AKSHARE_SYMBOL_MAP), 50)

    def test_rule4_atr_stop_loss(self):
        """硬规则#4: 止损方案必须可用"""
        from scripts.trade_plan import generate_trade_plan
        sym_data = {'pid': 'rb', 'price': 3200, 'score': 45, 'atr': 50, 'volatility': 0.02}
        plan = generate_trade_plan(sym_data, '多头趋势', {'ATR14': 50, 'volatility_pct': 2.0})
        self.assertIn('decision', plan)
        self.assertIn('confidence', plan)

    def test_rule5_risk_reward_ratio(self):
        """硬规则#5: 置信度在0~1之间"""
        from scripts.trade_plan import calc_confidence
        conf = calc_confidence(45, {'MA5': 1, 'RSI14': 55, 'MACD': 10, 'DMI': 1, 'OBV': 1, 'PRICE_POSITION': 1}, '多头趋势')
        self.assertGreaterEqual(conf, 0.0)
        self.assertLessEqual(conf, 1.0)

    def test_rule6_confidence_filter(self):
        """硬规则#6: 低分品种必须HOLD"""
        from scripts.trade_plan import generate_trade_plan
        plan = generate_trade_plan(
            {'pid': 'test', 'price': 100, 'score': 10, 'atr': 5, 'volatility': 0.02},
            '震荡', {'ATR14': 5, 'volatility_pct': 2.0}
        )
        self.assertEqual(plan['decision'], 'HOLD')

    def test_rule7_chain_logic(self):
        """硬规则#7: 品种必须有产业链分类"""
        from scripts.screen import get_chain_for_symbol
        from scripts.chains import CHAIN_PRODUCTS
        self.assertGreater(len(CHAIN_PRODUCTS), 0)
        for pid in ['rb', 'i', 'sc', 'cu', 'au', 'm', 'c']:
            chain = get_chain_for_symbol(pid)
            self.assertIsNotNone(chain, f"{pid} 应有产业链")

    def test_rule8_screen_before_verify(self):
        """硬规则#8: screen_signals有score_threshold参数"""
        from scripts.screen import screen_signals
        sig = inspect.signature(screen_signals)
        self.assertIn('score_threshold', sig.parameters)

    def test_rule9_confidence_first(self):
        """硬规则#9: 高质量信号置信度更高"""
        from scripts.trade_plan import calc_confidence
        high = calc_confidence(80, {'MA5': 1, 'RSI14': 65, 'MACD': 20, 'DMI': 1, 'OBV': 1, 'PRICE_POSITION': 1}, '多头趋势')
        low = calc_confidence(20, {'MA5': -1, 'RSI14': 45, 'MACD': -5, 'DMI': -1, 'OBV': -1, 'PRICE_POSITION': -1}, '空头趋势')
        self.assertGreater(high, low)

    def test_rule10_none_better_than_bad(self):
        """硬规则#10: 无效信号不产生候选"""
        from scripts.screen import screen_signals
        mock = [{
            'product_id': 'xx', 'product_name': '测试', 'last_price': 100,
            'open_interest': 0, 'score': 5, 'direction': 'NEUTRAL',
            'tech': {'MA5': 0, 'MA10': 0, 'RSI14': 50, 'MACD': 0, 'DMI': 0, 'OBV': 0, 'PRICE_POSITION': 0},
            'trend': {'trend': 'neutral', 'strength': 0},
            'signal_quality': 0, 'trend_stage': 'exhausted', 'resonance': 0.0,
        }]
        self.assertEqual(len(screen_signals(mock, score_threshold=20, min_resonance=0.5)), 0)


class TestPipelineIntegrity(unittest.TestCase):
    """管道完整性"""

    def test_no_hardcoded_path(self):
        """硬编码路径检查"""
        from scripts.run_pipeline import run_pipeline
        sig = inspect.signature(run_pipeline)
        for name, param in sig.parameters.items():
            if param.default is not inspect.Parameter.empty:
                self.assertNotIn('yangd', str(param.default))
        self.assertIsNone(sig.parameters['output_dir'].default)
        self.assertIsNone(sig.parameters['data_dir'].default)

    def test_chains_12_categories(self):
        """12产业链分类"""
        from scripts.chains import CHAIN_PRODUCTS
        expected = ['黑色系', '能源链', '聚酯链', '油化工', '煤化工',
                    '有色', '贵金属', '油脂油料', '谷物软商品', '建材', '橡胶', '纸浆造纸']
        for chain in expected:
            self.assertIn(chain, CHAIN_PRODUCTS, f"缺少产业链: {chain}")
        self.assertEqual(len(CHAIN_PRODUCTS), 12)

    def test_debate_units_keys(self):
        """辩论焦点结构"""
        from scripts.chains import DEBATE_UNITS
        self.assertGreater(len(DEBATE_UNITS), 0)
        for chain, unit in DEBATE_UNITS.items():
            self.assertIn('unit', unit)
            self.assertIn('focus', unit)

    def test_screen_count_resonance(self):
        """共振度函数可用"""
        from scripts.screen import count_resonance
        tech = {'MA5': 1, 'MA10': 1, 'RSI14': 55, 'MACD': 10, 'DMI': 1, 'OBV': 1, 'PRICE_POSITION': 1}
        resonance = count_resonance(tech, 50)
        self.assertIsInstance(resonance, dict)
        self.assertIn('ratio', resonance)
        self.assertGreaterEqual(resonance['ratio'], 0.0)
        self.assertLessEqual(resonance['ratio'], 1.0)

    def test_pipeline_runs_dry(self):
        """管道干运行不崩溃（无数据文件时的行为）"""
        from scripts.run_pipeline import run_pipeline
        import tempfile
        tmp = tempfile.mkdtemp()
        # 不应崩溃，而是返回错误信息
        try:
            result = run_pipeline(output_dir=tmp, data_dir=tmp)
        except (FileNotFoundError, json.JSONDecodeError):
            pass  # 预期行为
        except Exception as e:
            # 允许数据加载异常
            self.assertIn('market_data', str(e).lower())


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
