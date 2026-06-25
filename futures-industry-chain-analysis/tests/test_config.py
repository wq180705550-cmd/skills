# -*- coding: utf-8 -*-
"""config.py 单元测试 - 100%覆盖。"""

import sys
import os
import unittest

# 确保 scripts 目录在 path 中
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scripts.config import (
    CONFIG_MANAGER, CHAIN_TYPE_MAPPING, CHAIN_THRESHOLD_MAPPING,
    INDICATOR_CONFIG, ADAPTIVE_WEIGHT_SYSTEM, PRODUCT_THRESHOLDS,
    MARKET_STATE_SYSTEM,
    get_product_type, get_product_thresholds, get_adaptive_weights,
    calculate_position_size, calculate_atr_stop_loss,
    get_chain_debate_weight, get_atr_adaptive_thresholds,
)


class TestConfigManager(unittest.TestCase):

    def test_config_has_required_keys(self):
        for key in ['system', 'adaptive_weights', 'product_thresholds',
                     'market_state', 'trading', 'risk',
                     'chain_specific_indicators', 'chain_debate_weights']:
            self.assertIn(key, CONFIG_MANAGER)

    def test_system_version(self):
        self.assertEqual(CONFIG_MANAGER['system']['version'], '2.8')

    def test_min_open_interest(self):
        self.assertEqual(CONFIG_MANAGER['system']['min_open_interest'], 10000)

    def test_default_weights_sum_positive(self):
        w = CONFIG_MANAGER['adaptive_weights']['default_weights']
        self.assertGreater(sum(w.values()), 0)
        # 权重总和可能不等于100（get_adaptive_weights会归一化）
        for k, v in w.items():
            self.assertGreater(v, 0)

    def test_chain_type_mapping_coverage(self):
        all_chains = ['黑色系', '能源链', '聚酯链', '油化工', '煤化工',
                      '有色', '贵金属', '油脂油料', '谷物软商品', '建材', '橡胶', '纸浆造纸']
        for c in all_chains:
            self.assertIn(c, CHAIN_TYPE_MAPPING)

    def test_chain_threshold_mapping_coverage(self):
        all_chains = ['黑色系', '能源链', '聚酯链', '油化工', '煤化工',
                      '有色', '贵金属', '油脂油料', '谷物软商品', '建材', '橡胶', '纸浆造纸']
        for c in all_chains:
            self.assertIn(c, CHAIN_THRESHOLD_MAPPING)

    def test_indicator_config_keys(self):
        for key in ['MA', 'MACD', 'RSI', 'DMI', 'ATR', 'VOLUME', 'PRICE_POSITION']:
            self.assertIn(key, INDICATOR_CONFIG)

    def test_debate_weights_all_chains(self):
        for c in CHAIN_TYPE_MAPPING:
            if c in CONFIG_MANAGER['chain_debate_weights']:
                w = CONFIG_MANAGER['chain_debate_weights'][c]
                for k in ['technical_weight', 'fundamental_weight', 'chain_logic_weight', 'macro_weight']:
                    self.assertIn(k, w)
                    self.assertGreater(w[k], 0)


class TestGetProductType(unittest.TestCase):

    def test_industrial(self):
        self.assertEqual(get_product_type('黑色系'), 'industrial')

    def test_precious(self):
        self.assertEqual(get_product_type('贵金属'), 'precious')

    def test_agricultural(self):
        self.assertEqual(get_product_type('油脂油料'), 'agricultural')

    def test_unknown_defaults_to_industrial(self):
        self.assertEqual(get_product_type('未知产业链'), 'industrial')

    def test_nonferrous(self):
        self.assertEqual(get_product_type('有色'), 'nonferrous')


class TestGetProductThresholds(unittest.TestCase):

    def test_black(self):
        t = get_product_thresholds('黑色系')
        self.assertEqual(t['volatility_threshold'], 2.5)

    def test_energy(self):
        t = get_product_thresholds('能源链')
        self.assertEqual(t['volatility_threshold'], 3.0)

    def test_precious(self):
        t = get_product_thresholds('贵金属')
        self.assertEqual(t['volatility_threshold'], 2.0)

    def test_unknown_defaults(self):
        t = get_product_thresholds('未知')
        self.assertEqual(t, PRODUCT_THRESHOLDS['default'])


class TestGetAdaptiveWeights(unittest.TestCase):

    def test_sum_to_100(self):
        w = get_adaptive_weights('industrial', 'trending')
        self.assertAlmostEqual(sum(w.values()), 100, delta=2)

    def test_trending_boosts_dmi(self):
        w_t = get_adaptive_weights('industrial', 'trending')
        w_r = get_adaptive_weights('industrial', 'ranging')
        self.assertGreater(w_t.get('DMI', 0), w_r.get('DMI', 0))

    def test_ranging_boosts_rsi(self):
        w_r = get_adaptive_weights('industrial', 'ranging')
        w_t = get_adaptive_weights('industrial', 'trending')
        self.assertGreater(w_r.get('RSI', 0), w_t.get('RSI', 0))

    def test_agricultural_type(self):
        w = get_adaptive_weights('agricultural', 'trending')
        self.assertIsNotNone(w)

    def test_unknown_market_state(self):
        w = get_adaptive_weights('industrial', 'unknown_state')
        self.assertAlmostEqual(sum(w.values()), 100, delta=2)


class TestCalculatePositionSize(unittest.TestCase):

    def test_high_confidence_low_vol(self):
        p = calculate_position_size('高', 'low')
        val = float(p.replace('%', ''))
        self.assertGreater(val, 5)

    def test_low_confidence_high_vol(self):
        p = calculate_position_size('低', 'high')
        val = float(p.replace('%', ''))
        self.assertLess(val, 5)

    def test_medium_confidence(self):
        p = calculate_position_size('中', 'normal')
        val = float(p.replace('%', ''))
        self.assertGreaterEqual(val, 2)
        self.assertLessEqual(val, 8)

    def test_max_position_cap(self):
        p = calculate_position_size('高', 'low')
        val = float(p.replace('%', ''))
        self.assertLessEqual(val, 8)

    def test_min_position_floor(self):
        p = calculate_position_size('低', 'high')
        val = float(p.replace('%', ''))
        self.assertGreaterEqual(val, 2)


class TestCalculateATRStopLoss(unittest.TestCase):

    def test_buy_with_atr(self):
        sl = calculate_atr_stop_loss(3500, 50, 'BUY')
        self.assertLess(sl, 3500)
        self.assertAlmostEqual(sl, 3400, delta=1)

    def test_sell_with_atr(self):
        sl = calculate_atr_stop_loss(3500, 50, 'SELL')
        self.assertGreater(sl, 3500)
        self.assertAlmostEqual(sl, 3600, delta=1)

    def test_buy_zero_atr(self):
        sl = calculate_atr_stop_loss(3500, 0, 'BUY')
        self.assertAlmostEqual(sl, 3325, delta=1)

    def test_sell_zero_atr(self):
        sl = calculate_atr_stop_loss(3500, 0, 'SELL')
        self.assertAlmostEqual(sl, 3675, delta=1)


class TestGetChainDebateWeight(unittest.TestCase):

    def test_known_chain(self):
        w = get_chain_debate_weight('黑色系')
        self.assertIn('technical_weight', w)

    def test_unknown_chain_defaults(self):
        w = get_chain_debate_weight('不存在的链')
        self.assertEqual(w['technical_weight'], 1.0)


class TestGetATRAdaptiveThresholds(unittest.TestCase):

    def test_low_volatility(self):
        t = get_atr_adaptive_thresholds('贵金属', 0.5)
        self.assertLess(abs(t['strong_bullish']), 30)

    def test_high_volatility(self):
        t = get_atr_adaptive_thresholds('黑色系', 4.0)
        self.assertGreater(abs(t['strong_bullish']), 30)

    def test_normal_volatility(self):
        t = get_atr_adaptive_thresholds('聚酯链', 2.0)
        self.assertIn('strong_bullish', t)


if __name__ == '__main__':
    unittest.main()
