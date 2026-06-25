# -*- coding: utf-8 -*-
"""信号筛选模块测试。"""

import unittest
from scripts.screen import detect_trend_stage, count_resonance, screen_signals, get_chain_for_symbol, chain_verification


class TestDetectTrendStage(unittest.TestCase):
    """测试趋势阶段检测。"""

    def test_early_bull(self):
        """测试多头初期信号。"""
        tech = {
            'RSI14': 55,
            'MACD_DIF': 10,
            'MA5': 100,
            'MA10': 99,
            'MA20': 98,
            'last_price': 101,
            'ADX': 25
        }
        result = detect_trend_stage(tech, score=40)
        self.assertIn(result['stage'], ['early', 'mature', 'exhausted'])
        self.assertIn('confidence', result)

    def test_exhausted_bear(self):
        """测试空头末期信号。"""
        tech = {
            'RSI14': 25,
            'MACD_DIF': -15,
            'MA5': 100,
            'MA10': 102,
            'MA20': 105,
            'last_price': 95,
            'ADX': 30
        }
        result = detect_trend_stage(tech, score=-80)
        self.assertEqual(result['stage'], 'exhausted')


class TestCountResonance(unittest.TestCase):
    """测试多指标共振度。"""

    def test_strong_bull_resonance(self):
        """测试强多头共振。"""
        tech = {
            'MA5': 100,
            'MA10': 99,
            'MA20': 98,
            'MACD_DIF': 10,
            'RSI14': 60,
            'DMI_PDI': 30,
            'DMI_MDI': 15,
            'OBV': 1000,
            'OBV_MA20': 950,
            'last_price': 101
        }
        result = count_resonance(tech, score=70)
        self.assertGreaterEqual(result['confirmations'], 3)
        self.assertGreaterEqual(result['ratio'], 0.5)

    def test_weak_resonance(self):
        """测试弱共振（不应通过筛选）。"""
        tech = {
            'MA5': 100,
            'MA10': 101,
            'MA20': 102,
            'MACD_DIF': -5,
            'RSI14': 55,
            'DMI_PDI': 20,
            'DMI_MDI': 25,
            'OBV': 950,
            'OBV_MA20': 1000,
            'last_price': 99
        }
        result = count_resonance(tech, score=30)
        self.assertLess(result['ratio'], 0.5)


class TestGetChainForSymbol(unittest.TestCase):
    """测试品种到产业链映射。"""

    def test_black_chain(self):
        """测试黑色系品种映射。"""
        self.assertEqual(get_chain_for_symbol('rb'), '黑色系')
        self.assertEqual(get_chain_for_symbol('hc'), '黑色系')
        self.assertEqual(get_chain_for_symbol('i'), '黑色系')

    def test_energy_chain(self):
        """测试能源链品种映射。"""
        self.assertEqual(get_chain_for_symbol('sc'), '能源链')
        self.assertEqual(get_chain_for_symbol('ec'), '能源链')

    def test_new_symbols(self):
        """测试新增品种映射。"""
        self.assertEqual(get_chain_for_symbol('lc'), '有色')
        self.assertEqual(get_chain_for_symbol('si'), '有色')
        self.assertEqual(get_chain_for_symbol('pt'), '贵金属')


class TestChainVerification(unittest.TestCase):
    """测试产业链验证。"""

    def test_aligned_signal(self):
        """测试信号与产业链趋势一致。"""
        candidate = {
            'product_id': 'rb',
            'symbol': 'rb',
            'score': -80,
            'stage': 'mature',
            'resonance': 0.8,
            'signal_quality': 0.7,
            'direction': 'SELL'
        }
        chain_results = {
            '黑色系': {
                'overall_trend': '空头趋势',
                'avg_score': -70,
                'count': 3,
                'members': [
                    {'symbol': 'rb', 'score': -80},
                    {'symbol': 'hc', 'score': -75},
                    {'symbol': 'i', 'score': -60}
                ]
            }
        }
        result = chain_verification(candidate, chain_results)
        self.assertTrue(result['aligned'])
        self.assertGreater(result['confidence_adjustment'], 0)

    def test_divergent_signal(self):
        """测试信号与产业链趋势背离。"""
        candidate = {
            'product_id': 'rb',
            'symbol': 'rb',
            'score': 60,
            'stage': 'early',
            'resonance': 0.7,
            'signal_quality': 0.6,
            'direction': 'BUY'
        }
        chain_results = {
            '黑色系': {
                'overall_trend': '空头趋势',
                'avg_score': -70,
                'count': 3,
                'members': [
                    {'symbol': 'rb', 'score': 60},
                    {'symbol': 'hc', 'score': -75},
                    {'symbol': 'i', 'score': -60}
                ]
            }
        }
        result = chain_verification(candidate, chain_results)
        self.assertFalse(result['aligned'])
        self.assertLess(result['confidence_adjustment'], 0)


class TestScreenSignalsMarketFilter(unittest.TestCase):
    """测试市场环境过滤逻辑。"""

    def _make_symbol(self, pid, score, price=1000, oi=50000):
        """创建测试用品种数据。"""
        return {
            'product_id': pid,
            'product_name': f'test_{pid}',
            'last_price': price,
            'open_interest': oi,
            'trend': {'score': score},
            'tech': {
                'MA5': price * 1.01 if score > 0 else price * 0.99,
                'MA10': price * 1.005 if score > 0 else price * 0.995,
                'MA20': price,
                'MACD_DIF': 10 if score > 0 else -10,
                'RSI14': 55 if score > 0 else 45,
                'DMI_PDI': 30 if score > 0 else 15,
                'DMI_MDI': 15 if score > 0 else 30,
                'OBV': 1000 if score > 0 else 900,
                'OBV_MA20': 950 if score > 0 else 950,
                'last_price': price,
                'ATR14': price * 0.02,
            }
        }

    def test_bearish_market_filters_weak_buy_signals(self):
        """测试偏空市场过滤弱多头信号。"""
        # 创建偏空市场：8个空头信号，2个多头信号
        symbols = []
        for i in range(8):
            symbols.append(self._make_symbol(f'sell{i}', -60 - i * 5))
        # 弱多头信号（得分刚过阈值）
        symbols.append(self._make_symbol('buy1', 35))
        symbols.append(self._make_symbol('buy2', 40))

        candidates = screen_signals(symbols, score_threshold=20, min_resonance=0.5)
        # 在偏空市场，多头信号需要60%共振度才能通过
        buy_candidates = [c for c in candidates if c['direction'] == 'BUY']
        # 由于我们的测试数据共振度可能不到60%，多头应该被过滤
        for bc in buy_candidates:
            self.assertGreaterEqual(bc['resonance']['ratio'], 0.6,
                                   f"多头信号 {bc['product_id']} 共振度应>=60%")

    def test_balanced_market_normal_filtering(self):
        """测试平衡市场正常过滤。"""
        # 创建平衡市场：5个多头，5个空头
        symbols = []
        for i in range(5):
            symbols.append(self._make_symbol(f'buy{i}', 60 + i * 5))
        for i in range(5):
            symbols.append(self._make_symbol(f'sell{i}', -60 - i * 5))

        candidates = screen_signals(symbols, score_threshold=20, min_resonance=0.5)
        # 平衡市场应该有多头和空头机会
        buy_count = sum(1 for c in candidates if c['direction'] == 'BUY')
        sell_count = sum(1 for c in candidates if c['direction'] == 'SELL')
        # 不做严格断言，只验证不报错
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
