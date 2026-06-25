# -*- coding: utf-8 -*-
"""report.py 单元测试 - 100%覆盖。"""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scripts.report import generate_markdown_report, generate_html_report


def _make_test_data():
    chain_results = {
        '黑色系': {
            'count': 5, 'leader': 'rb', 'leader_price': 3500.0,
            'overall_trend': '空头趋势', 'avg_score': -30.0,
            'leader_reason': '趋势得分最低（领跌）',
            'debate_unit': {'focus': '成本推涨vs需求拉动'},
            'members': [
                {'pid': 'rb', 'price': 3500.0, 'score': -40, 'trend': 'strong_bear', 'oi': 50000},
            ],
        },
    }
    debate_results = {
        '黑色系': {
            'bull': {'strength': 5, 'arguments': []},
            'bear': {'strength': 15, 'arguments': []},
            'decision': {'verdict': 'SELL', 'plan': '逢高做空'},
        },
    }
    trade_plans = {
        '黑色系': {
            'decision': 'SELL', 'pid': 'rb', 'entry_price': 3500.0,
            'target_price': 3360.0, 'stop_loss': 3600.0,
            'risk_reward_ratio': 1.4, 'confidence': 0.65,
            'recommend_score': 0.595, 'position_size': '5.0%', 'validity': '1-3日',
        },
    }
    risk_assessments = {
        '黑色系': {
            'risk_decision': {'risk_score': 6.0, 'final_decision': 'SELL', 'position_adjustment': '维持原仓位'},
        },
    }
    return chain_results, debate_results, trade_plans, risk_assessments


class TestGenerateMarkdownReport(unittest.TestCase):

    def test_basic_structure(self):
        cr, dr, tp, ra = _make_test_data()
        md = generate_markdown_report(cr, dr, tp, ra)
        self.assertIn('商品期货产业链分析报告', md)
        self.assertIn('黑色系', md)
        self.assertIn('rb', md)

    def test_contains_trade_plan(self):
        cr, dr, tp, ra = _make_test_data()
        md = generate_markdown_report(cr, dr, tp, ra)
        self.assertIn('做空', md)
        self.assertIn('3500.00', md)

    def test_disclaimer_present(self):
        cr, dr, tp, ra = _make_test_data()
        md = generate_markdown_report(cr, dr, tp, ra)
        self.assertIn('仅供参考', md)

    def test_hold_trade(self):
        cr, dr, tp, ra = _make_test_data()
        tp['黑色系'] = {'decision': 'HOLD', 'confidence': 0, 'recommend_score': 0}
        md = generate_markdown_report(cr, dr, tp, ra)
        self.assertIn('观望', md)


class TestGenerateHtmlReport(unittest.TestCase):

    def test_basic_structure(self):
        cr, dr, tp, ra = _make_test_data()
        html = generate_html_report(cr, dr, tp, ra)
        self.assertIn('<!DOCTYPE html>', html)
        self.assertIn('chart.js', html)

    def test_contains_chartjs(self):
        cr, dr, tp, ra = _make_test_data()
        html = generate_html_report(cr, dr, tp, ra)
        self.assertIn('chart.js', html)

    def test_contains_decision_stats(self):
        cr, dr, tp, ra = _make_test_data()
        html = generate_html_report(cr, dr, tp, ra)
        self.assertIn('SELL', html)

    def test_contains_members(self):
        cr, dr, tp, ra = _make_test_data()
        html = generate_html_report(cr, dr, tp, ra)
        self.assertIn('rb', html)

    def test_disclaimer(self):
        cr, dr, tp, ra = _make_test_data()
        html = generate_html_report(cr, dr, tp, ra)
        self.assertIn('仅供参考', html)

    def test_hold_card(self):
        cr, dr, tp, ra = _make_test_data()
        tp['黑色系'] = {'decision': 'HOLD', 'confidence': 0, 'recommend_score': 0}
        html = generate_html_report(cr, dr, tp, ra)
        self.assertIn('观望', html)


if __name__ == '__main__':
    unittest.main()
