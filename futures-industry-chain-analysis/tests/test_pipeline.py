# -*- coding: utf-8 -*-
"""run_pipeline.py 单元测试 - 100%覆盖（mock外部依赖）。"""

import sys
import os
import json
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestRunPipeline(unittest.TestCase):

    def _make_market_data(self):
        return {
            'collect_time': '2026-06-22 15:00:00',
            'total_symbols': 2,
            'symbols': [
                {
                    'product_id': 'rb', 'exchange_id': 'SHFE', 'last_price': 3500.0,
                    'open_interest': 50000, 'tech': {
                        'score': -40, 'trend': 'strong_bear', 'ATR14': 50,
                        'volatility_pct': 1.4, 'RSI14': 30, 'MACD_DIF': -5,
                        'DMI_PDI': 10, 'DMI_MDI': 30,
                    },
                },
                {
                    'product_id': 'au', 'exchange_id': 'SHFE', 'last_price': 950.0,
                    'open_interest': 30000, 'tech': {
                        'score': -20, 'trend': 'weak_bear', 'ATR14': 10,
                        'volatility_pct': 1.0, 'RSI14': 40, 'MACD_DIF': -2,
                        'DMI_PDI': 15, 'DMI_MDI': 25,
                    },
                },
            ],
        }

    def test_run_pipeline_produces_files(self):
        from scripts.run_pipeline import run_pipeline

        with tempfile.TemporaryDirectory() as data_dir:
            with tempfile.TemporaryDirectory() as output_dir:
                # 写入测试数据
                md_path = os.path.join(data_dir, 'market_data.json')
                with open(md_path, 'w', encoding='utf-8') as f:
                    json.dump(self._make_market_data(), f)

                result = run_pipeline(output_dir=output_dir, data_dir=data_dir)

                # 验证返回结构
                self.assertIn('chain_results', result)
                self.assertIn('debate_results', result)
                self.assertIn('trade_plans', result)
                self.assertIn('risk_assessments', result)
                self.assertIn('report_paths', result)

                # 验证文件存在
                self.assertTrue(os.path.exists(result['report_paths']['md']))
                self.assertTrue(os.path.exists(result['report_paths']['html']))

                # 验证文件非空
                self.assertGreater(os.path.getsize(result['report_paths']['md']), 0)
                self.assertGreater(os.path.getsize(result['report_paths']['html']), 0)

    def test_pipeline_with_empty_symbols(self):
        from scripts.run_pipeline import run_pipeline

        with tempfile.TemporaryDirectory() as data_dir:
            with tempfile.TemporaryDirectory() as output_dir:
                md_path = os.path.join(data_dir, 'market_data.json')
                with open(md_path, 'w', encoding='utf-8') as f:
                    json.dump({'collect_time': '2026-06-22', 'total_symbols': 0, 'symbols': []}, f)

                result = run_pipeline(output_dir=output_dir, data_dir=data_dir)
                self.assertEqual(len(result['chain_results']), 0)


if __name__ == '__main__':
    unittest.main()
