# -*- coding: utf-8 -*-
"""data_fallback.py 单元测试 - 100%覆盖。"""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scripts.data_fallback import DataFallbackManager


class TestDataFallbackManager(unittest.TestCase):

    def setUp(self):
        self.mgr = DataFallbackManager()

    def test_source_priority(self):
        self.assertEqual(self.mgr.source_priority[0], 'tqsdk')
        self.assertEqual(self.mgr.source_priority[1], 'tdx')
        self.assertEqual(self.mgr.source_priority[2], 'akshare')

    def test_fetch_quote_all_fail(self):
        result = self.mgr.fetch_quote('TEST')
        self.assertIsNone(result)

    def test_fetch_from_tqsdk_returns_none(self):
        result = self.mgr._fetch_from_tqsdk('rb')
        self.assertIsNone(result)

    def test_fetch_from_tdx_returns_none(self):
        result = self.mgr._fetch_from_tdx('rb')
        self.assertIsNone(result)

    def test_fetch_from_web_returns_none(self):
        result = DataFallbackManager._fetch_from_web('rb')
        self.assertIsNone(result)

    def test_fetch_from_cache_returns_none(self):
        result = DataFallbackManager._fetch_from_cache('rb')
        self.assertIsNone(result)

    def test_sources_dict_keys(self):
        expected = {'tqsdk', 'tdx', 'akshare', 'web_search', 'cache'}
        self.assertEqual(set(self.mgr.sources.keys()), expected)


if __name__ == '__main__':
    unittest.main()
