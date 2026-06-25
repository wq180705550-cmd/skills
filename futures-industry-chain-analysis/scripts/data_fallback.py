# -*- coding: utf-8 -*-
"""数据降级策略管理器。

降级优先级：TqSdk → AKShare → Cache
通达信 MCP 对期货数据支持有限，不纳入自动降级链。
"""

import json
import os
import time
from typing import Optional, List, Dict


# AKShare 期货代码映射（主力连续合约格式，全部小写）
_AKSHARE_SYMBOL_MAP: Dict[str, str] = {
    'rb': 'rb0', 'hc': 'hc0', 'i': 'i0', 'j': 'j0', 'jm': 'jm0',
    'SF': 'sf0', 'SM': 'sm0',
    'sc': 'sc0', 'lu': 'lu0', 'fu': 'fu0', 'bu': 'bu0', 'pg': 'pg0',
    'PX': 'px0', 'TA': 'ta0', 'PF': 'pf0', 'PR': 'pr0',
    'eg': 'eg0', 'eb': 'eb0', 'v': 'v0', 'pp': 'pp0', 'l': 'l0',
    'MA': 'ma0', 'SH': 'sh0',
    'cu': 'cu0', 'al': 'al0', 'zn': 'zn0', 'pb': 'pb0', 'ni': 'ni0',
    'sn': 'sn0', 'ao': 'ao0', 'SS': 'ss0',
    'au': 'au0', 'ag': 'ag0',
    'a': 'a0', 'b': 'b0', 'm': 'm0', 'y': 'y0', 'p': 'p0',
    'OI': 'oi0', 'RM': 'rm0', 'PK': 'pk0',
    'c': 'c0', 'cs': 'cs0', 'SR': 'sr0', 'CF': 'cf0',
    'jd': 'jd0', 'lh': 'lh0', 'AP': 'ap0', 'CJ': 'cj0',
    'FG': 'fg0', 'SA': 'sa0', 'UR': 'ur0',
    'ru': 'ru0', 'nr': 'nr0', 'br': 'br0',
    'sp': 'sp0', 'op': 'op0',
    # 新增品种（持仓量 > 10000）
    'lc': 'lc0', 'si': 'si0', 'ps': 'ps0', 'ec': 'ec0',
    'rr': 'rr0', 'PL': 'pl0', 'ad': 'ad0', 'CY': 'cy0',
    'bz': 'bz0', 'pt': 'pt0',
}


class DataFallbackManager:
    """数据降级管理器：多数据源容错。

    降级优先级：TqSdk → AKShare(futures_main_sina) → Cache
    """

    def __init__(self, cache_dir: str = None):
        self.cache_dir = cache_dir or os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'cache'
        )
        os.makedirs(self.cache_dir, exist_ok=True)

        self.sources = {
            'tqsdk': self._fetch_from_tqsdk,
            'akshare': self._fetch_from_akshare,
            'cache': self._fetch_from_cache,
        }
        self.source_priority = ['tqsdk', 'akshare', 'cache']

    def fetch_quote(self, symbol: str) -> Optional[dict]:
        """获取行情数据（带降级）。"""
        for source_name in self.source_priority:
            try:
                data = self.sources[source_name](symbol)
                if data and data.get('last_price', 0) > 0:
                    return {'data': data, 'source': source_name}
            except Exception as e:
                print(f"  [WARN] {source_name} 获取 {symbol} 失败: {e}")
                continue
        return None

    def fetch_klines(self, symbol: str, days: int = 80) -> Optional[List[dict]]:
        """获取K线数据（带降级）。返回 [{open, high, low, close, volume, open_interest}, ...]"""
        for source_name in ['tqsdk', 'akshare', 'cache']:
            try:
                if source_name == 'tqsdk':
                    data = self._fetch_klines_tqsdk(symbol, days)
                elif source_name == 'akshare':
                    data = self._fetch_klines_akshare(symbol, days)
                else:
                    data = self._fetch_klines_cache(symbol, days)
                if data and len(data) > 0:
                    return data
            except Exception as e:
                print(f"  [WARN] {source_name} K线 {symbol} 失败: {e}")
                continue
        return None

    @staticmethod
    def _fetch_from_tqsdk(symbol: str) -> Optional[dict]:
        """从TqSdk获取实时行情。需要 TQSDK_USERNAME/TQSDK_PASSWORD 或 TQ_USER/TQ_PASSWORD 环境变量。"""
        tq_user = os.environ.get('TQSDK_USERNAME') or os.environ.get('TQ_USER')
        tq_password = os.environ.get('TQSDK_PASSWORD') or os.environ.get('TQ_PASSWORD')
        if not tq_user or not tq_password:
            return None

        try:
            from tqsdk import TqApi, TqAuth
            # 此处需要知道交易所，简化处理：尝试所有交易所
            # 实际使用时由 collect_data.py 统一调用 TqApi
            return None  # 单品种查询效率低，建议用 collect_data.py 批量获取
        except ImportError:
            return None

    def _fetch_from_akshare(self, symbol: str) -> Optional[dict]:
        """从AKShare获取期货行情（通过 futures_main_sina）。"""
        try:
            import akshare as ak
        except ImportError:
            print("  [ERROR] AKShare 未安装")
            return None

        ak_symbol = _AKSHARE_SYMBOL_MAP.get(symbol, symbol + '0')
        try:
            from datetime import datetime, timedelta
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=5)).strftime('%Y%m%d')
            df = ak.futures_main_sina(symbol=ak_symbol, start_date=start_date, end_date=end_date)
            if df is None or df.empty:
                return None

            last = df.iloc[-1]
            prev = df.iloc[-2] if len(df) > 1 else last
            last_price = float(last['收盘价'])
            prev_close = float(prev['收盘价'])
            change_pct = round((last_price / prev_close - 1) * 100, 2) if prev_close > 0 else 0

            return {
                'last_price': last_price,
                'open_interest': int(last.get('持仓量', 0) or 0),
                'change_pct': change_pct,
                'open': float(last.get('开盘价', 0) or 0),
                'high': float(last.get('最高价', 0) or 0),
                'low': float(last.get('最低价', 0) or 0),
                'volume': int(last.get('成交量', 0) or 0),
                'settlement': float(last.get('动态结算价', 0) or 0),
            }
        except Exception as e:
            print(f"  [WARN] AKShare 获取 {symbol} 失败: {e}")
            return None

    def _fetch_klines_akshare(self, symbol: str, days: int = 80) -> Optional[List[dict]]:
        """从AKShare获取K线数据。"""
        try:
            import akshare as ak
        except ImportError:
            return None

        ak_symbol = _AKSHARE_SYMBOL_MAP.get(symbol, symbol + '0')
        try:
            from datetime import datetime, timedelta
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=days + 30)).strftime('%Y%m%d')  # 多取30天缓冲
            df = ak.futures_main_sina(symbol=ak_symbol, start_date=start_date, end_date=end_date)
            if df is None or df.empty:
                return None

            klines = []
            for _, row in df.iterrows():
                klines.append({
                    'date': str(row.get('日期', '')),
                    'open': float(row.get('开盘价', 0) or 0),
                    'high': float(row.get('最高价', 0) or 0),
                    'low': float(row.get('最低价', 0) or 0),
                    'close': float(row.get('收盘价', 0) or 0),
                    'volume': int(row.get('成交量', 0) or 0),
                    'open_interest': int(row.get('持仓量', 0) or 0),
                })

            # 缓存到本地
            self._save_cache(symbol, klines)

            return klines[-days:] if len(klines) > days else klines
        except Exception as e:
            print(f"  [WARN] AKShare K线 {symbol} 失败: {e}")
            return None

    def _fetch_from_cache(self, symbol: str) -> Optional[dict]:
        """从本地缓存获取数据。"""
        cache_file = os.path.join(self.cache_dir, f'{symbol}_quote.json')
        if not os.path.exists(cache_file):
            return None
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            # 检查缓存是否过期（24小时）
            cached_time = data.get('_cached_at', 0)
            if time.time() - cached_time > 86400:
                return None
            return data
        except Exception:
            return None

    def _fetch_klines_cache(self, symbol: str, days: int = 80) -> Optional[List[dict]]:
        """从本地缓存获取K线数据。"""
        cache_file = os.path.join(self.cache_dir, f'{symbol}_klines.json')
        if not os.path.exists(cache_file):
            return None
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            cached_time = data.get('_cached_at', 0)
            if time.time() - cached_time > 86400:
                return None
            return data.get('klines', [])[-days:]
        except Exception:
            return None

    def _save_cache(self, symbol: str, klines: List[dict]):
        """保存K线数据到缓存。"""
        try:
            cache_file = os.path.join(self.cache_dir, f'{symbol}_klines.json')
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump({
                    '_cached_at': time.time(),
                    'klines': klines,
                }, f, ensure_ascii=False)
        except Exception:
            pass
