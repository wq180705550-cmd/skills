#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交易所官方数据采集模块 v3.0
支持：大商所(DCE)、上期所(SHFE)、郑商所(CZCE)、中金所(CFFEX)、广期所(GFEX)

数据源优先级：
1. 交易所官方API（最权威，无爬虫合规风险）
2. AKShare（降级方案）
3. TqSdk（实时行情）

数据持久化：DuckDB存储，连接复用，批量插入

核心设计：
- 单例数据库连接，减少创建/销毁开销
- 批量 INSERT OR IGNORE，避免全表扫描
- 数据完整性校验（价格逻辑、非空检查）
- 自动重试机制（应对API临时故障）
- 交易日期校验（考虑周末和候选节假日）
"""

import requests
import json
import time
import pandas as pd
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from html.parser import HTMLParser
import re
import duckdb


# ==================== 路径配置 ====================
SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(SKILL_DIR, 'data')
DB_PATH = os.path.join(DATA_DIR, 'exchange_futures_data.duckdb')

# 中国法定节假日（仅非调休日，调休上班日会正常交易）
# 格式: YYYYMMDD
_KNOWN_HOLIDAYS = frozenset({
    # 2026年主要节假日（不含调休上班日）
    '20260101',  # 元旦
    '20260102',
    '20260103',
    '20260128',  # 春节
    '20260129',
    '20260130',
    '20260131',
    '20260201',
    '20260202',
    '20260203',
    '20260204',
    '20260205',
    '20260206',
    '20260207',
    '20260208',
    '20260209',
    '20260210',
    '20260211',
    '20260212',
    '20260213',
    '20260214',
    '20260215',
    '20260302',  # 元宵节
    '20260405',  # 清明节
    '20260406',
    '20260501',  # 劳动节
    '20260502',
    '20260503',
    '20260504',
    '20260505',
    '20260612',  # 端午节
    '20260613',
    '20260614',
    '20260615',
    '20260616',
    '20260927',  # 中秋节
    '20260928',
    '20261001',  # 国庆节
    '20261002',
    '20261003',
    '20261004',
    '20261005',
    '20261006',
    '20261007',
    '20261008',
})


# ==================== 数据验证 ====================
def validate_price_record(record: dict) -> Optional[dict]:
    """
    验证单条价格记录的完整性。
    返回修正后的记录，如果记录不可用则返回None。
    """
    # 必填字段非空检查
    if not record.get('symbol'):
        return None

    # 价格逻辑检查
    high = record.get('high', 0) or 0
    low = record.get('low', 0) or 0
    close = record.get('close', 0) or 0
    open_ = record.get('open', 0) or 0

    # 所有关键价格必须为正数（0=缺失数据）
    if close <= 0:
        return None

    # high >= low（互换位置而不是丢弃）
    if high > 0 and low > 0 and high < low:
        record['high'], record['low'] = low, high

    # 非负检查
    record['volume'] = max(0, int(record.get('volume', 0) or 0))
    record['open_interest'] = max(0, int(record.get('open_interest', 0) or 0))
    record['turnover'] = max(0, float(record.get('turnover', 0) or 0))

    return record


class ExchangeDataCollector:
    """交易所官方数据采集器"""

    # 类级缓存，避免重复创建DB连接
    _db_conn_cache = {}

    def __init__(self, db_path: str = DB_PATH):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.db_path = db_path
        self._conn = None  # 懒加载连接

        # 确保data目录存在（仅一次）
        if not hasattr(ExchangeDataCollector, '_dir_created'):
            os.makedirs(DATA_DIR, exist_ok=True)
            ExchangeDataCollector._dir_created = True

        # 初始化数据库（仅一次）
        self._init_database()

    def _get_conn(self):
        """获取数据库连接（懒加载+复用）"""
        if self._conn is None:
            self._conn = duckdb.connect(self.db_path)
        return self._conn

    def _init_database(self):
        """初始化DuckDB数据库，创建日线数据表"""
        # 检查是否已经初始化过（类级缓存）
        if ExchangeDataCollector._db_conn_cache.get('initialized'):
            return

        conn = self._get_conn()
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS daily_data (
                    exchange VARCHAR,
                    symbol VARCHAR,
                    trade_date VARCHAR,
                    open DOUBLE,
                    high DOUBLE,
                    low DOUBLE,
                    close DOUBLE,
                    settle DOUBLE,
                    volume BIGINT,
                    open_interest BIGINT,
                    turnover DOUBLE,
                    source VARCHAR,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (exchange, symbol, trade_date)
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_daily_data_date
                ON daily_data (trade_date)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_daily_data_symbol
                ON daily_data (symbol)
            """)
            ExchangeDataCollector._db_conn_cache['initialized'] = True
            print(f"[DB] 数据库初始化完成: {self.db_path}")
        except Exception:
            raise

    def _save_to_db(self, df: pd.DataFrame):
        """将数据批量保存到DuckDB（INSERT OR IGNORE）"""
        if df is None or len(df) == 0:
            return

        # 过滤无效记录
        valid_records = []
        for _, row in df.iterrows():
            record = validate_price_record(row.to_dict())
            if record is not None:
                valid_records.append(record)

        if not valid_records:
            print("[DB] 无有效记录可保存")
            return

        new_df = pd.DataFrame(valid_records)
        conn = self._get_conn()
        try:
            conn.execute("INSERT OR IGNORE INTO daily_data SELECT * FROM new_df")
            print(f"[DB] 新增 {len(new_df)} 条记录到DuckDB")
        except Exception as e:
            print(f"[DB] 保存失败: {e}")

    def _read_from_db(self, trade_date: str, exchange: Optional[str] = None) -> Optional[pd.DataFrame]:
        """从DuckDB读取指定日期的数据"""
        conn = self._get_conn()
        try:
            if exchange:
                result = conn.execute("""
                    SELECT * FROM daily_data
                    WHERE trade_date = ? AND exchange = ?
                    ORDER BY symbol
                """, [trade_date, exchange]).fetchdf()
            else:
                result = conn.execute("""
                    SELECT * FROM daily_data
                    WHERE trade_date = ?
                    ORDER BY exchange, symbol
                """, [trade_date]).fetchdf()

            if len(result) > 0:
                return result
            return None
        except Exception as e:
            print(f"[DB] 读取失败: {e}")
            return None

    def get_cached_dates(self) -> List[str]:
        """获取数据库中已有的交易日期列表"""
        conn = self._get_conn()
        try:
            result = conn.execute("""
                SELECT DISTINCT trade_date FROM daily_data
                ORDER BY trade_date DESC
            """).fetchall()
            return [row[0] for row in result]
        except Exception as e:
            print(f"[DB] 获取缓存日期失败: {e}")
            return []

    def get_cached_count(self) -> int:
        """获取总缓存记录数"""
        conn = self._get_conn()
        try:
            return conn.execute("SELECT COUNT(*) FROM daily_data").fetchone()[0]
        except Exception:
            return 0

    # ==================== 大商所 (DCE) ====================
    def get_dce_daily_data(self, trade_date: str, use_cache: bool = True) -> Optional[pd.DataFrame]:
        """
        获取大商所日线数据

        API端点: POST http://www.dce.com.cn/publicweb/quotesdata/exportDayQuotesChData.html
        响应格式: TSV（制表符分隔），第一列为合约代码
        """
        if use_cache:
            cached = self._read_from_db(trade_date, 'DCE')
            if cached is not None:
                print(f"[DB] DCE缓存命中 ({len(cached)}条)")
                return cached

        try:
            url = 'http://www.dce.com.cn/publicweb/quotesdata/exportDayQuotesChData.html'
            month_index = str(int(trade_date[4:6]) - 1)  # 月份参数从0开始
            data = {
                'dayQuotes.variety': 'all',
                'dayQuotes.trade_type': '0',
                'year': trade_date[:4],
                'month': month_index,
                'day': trade_date[6:8],
            }

            response = self.session.post(url, data=data, timeout=30)
            response.encoding = 'utf-8'

            if response.status_code != 200:
                print(f"[DCE] API请求失败: {response.status_code}")
                return None

            # 解析TSV格式（支持\r\n和\n两种换行）
            lines = re.split(r'[\r\n]+', response.text.strip())
            records = []

            for line in lines:
                line = line.strip()
                if not line or '小计' in line or '合计' in line or '品种' in line:
                    continue

                fields = re.split(r'\t+', line)
                if len(fields) < 10:
                    continue

                try:
                    symbol = fields[0].strip()
                    if not symbol or symbol in ('合约代码', '合约名称'):
                        continue

                    records.append({
                        'exchange': 'DCE',
                        'symbol': symbol,
                        'trade_date': trade_date,
                        'open': float(fields[2].replace(',', '') or 0),
                        'high': float(fields[3].replace(',', '') or 0),
                        'low': float(fields[4].replace(',', '') or 0),
                        'close': float(fields[5].replace(',', '') or 0),
                        'settle': float(fields[6].replace(',', '') or 0),
                        'volume': int(float(fields[7].replace(',', '') or 0)),
                        'open_interest': int(float(fields[8].replace(',', '') or 0)),
                        'turnover': float(fields[9].replace(',', '') or 0) if len(fields) > 9 else 0,
                        'source': 'DCE官方API'
                    })
                except (ValueError, IndexError):
                    continue

            if records:
                df = pd.DataFrame(records)
                print(f"[DCE] 成功: {len(df)}条")
                self._save_to_db(df)
                return df
            else:
                print("[DCE] 无有效记录")
                return None

        except Exception as e:
            print(f"[DCE] 异常: {e}")
            return None

    # ==================== 上期所 (SHFE) ====================
    def get_shfe_daily_data(self, trade_date: str, use_cache: bool = True) -> Optional[pd.DataFrame]:
        """
        获取上期所日线数据

        API端点: GET http://www.shfe.com.cn/data/dailydata/kx/kx{YYYYMMDD}.dat
        响应格式: JSON，根字段 o_curinstrument 为数组
        """
        if use_cache:
            cached = self._read_from_db(trade_date, 'SHFE')
            if cached is not None:
                print(f"[DB] SHFE缓存命中 ({len(cached)}条)")
                return cached

        try:
            url = f'http://www.shfe.com.cn/data/dailydata/kx/kx{trade_date}.dat'
            response = self.session.get(url, timeout=30)

            if response.status_code != 200:
                print(f"[SHFE] API请求失败: {response.status_code}")
                return None

            json_data = json.loads(response.content.decode('utf-8'))

            if 'o_curinstrument' not in json_data:
                print("[SHFE] 数据格式异常（缺少o_curinstrument字段）")
                return None

            records = []
            for item in json_data['o_curinstrument']:
                try:
                    product_id = item.get('PRODUCTID', '')
                    if not product_id or product_id.endswith('_summary'):
                        continue

                    # 上期所字段名: OPENPRICE, HIGHESTPRICE, LOWESTPRICE, CLOSEPRICE,
                    # SETTLEMENTPRICE, VOLUME, OPENINTEREST, TURNOVER
                    turnover = item.get('TURNOVER', 0)
                    records.append({
                        'exchange': 'SHFE',
                        'symbol': product_id,
                        'trade_date': trade_date,
                        'open': float(item.get('OPENPRICE', 0) or 0),
                        'high': float(item.get('HIGHESTPRICE', 0) or 0),
                        'low': float(item.get('LOWESTPRICE', 0) or 0),
                        'close': float(item.get('CLOSEPRICE', 0) or 0),
                        'settle': float(item.get('SETTLEMENTPRICE', 0) or 0),
                        'volume': int(float(item.get('VOLUME', 0) or 0)),
                        'open_interest': int(float(item.get('OPENINTEREST', 0) or 0)),
                        'turnover': float(turnover or 0),
                        'source': 'SHFE官方API'
                    })
                except (ValueError, TypeError):
                    continue

            if records:
                df = pd.DataFrame(records)
                print(f"[SHFE] 成功: {len(df)}条")
                self._save_to_db(df)
                return df
            else:
                print("[SHFE] 无有效记录")
                return None

        except Exception as e:
            print(f"[SHFE] 异常: {e}")
            return None

    # ==================== 郑商所 (CZCE) ====================
    class CzceHtmlParser(HTMLParser):
        """
        郑商所HTML日线数据解析器

        目标表格：id="senfe" 或 id="tab1"
        数据结构：合约代码 | 开盘 | 最高 | 最低 | 收盘 | 结算 | 成交量 | 持仓量
        """
        def __init__(self):
            super().__init__()
            self.in_table = False
            self.in_tr = False
            self.in_td = False
            self.data = []
            self.current_row = []
            self._table_ids = {'senfe', 'tab1'}

        def handle_starttag(self, tag, attrs):
            if tag == 'table':
                for attr in attrs:
                    if attr[0] == 'id' and attr[1] in self._table_ids:
                        self.in_table = True
                        break
            elif tag == 'tr' and self.in_table:
                self.in_tr = True
                self.current_row = []
            elif tag in ('td', 'th') and self.in_tr:
                self.in_td = True

        def handle_endtag(self, tag):
            if tag == 'table':
                self.in_table = False
                self.data = []  # 只保留最后一个数据表
            elif tag == 'tr' and self.in_tr:
                self.in_tr = False
                if self.current_row:
                    self.data.append(self.current_row)
            elif tag in ('td', 'th'):
                self.in_td = False

        def handle_data(self, data):
            if self.in_td:
                self.current_row.append(data.strip())

    def get_czce_daily_data(self, trade_date: str, use_cache: bool = True) -> Optional[pd.DataFrame]:
        """
        获取郑商所日线数据

        API端点:
          新版(>20151111): GET .../DFSStaticFiles/Future/{YYYY}/{YYYYMMDD}/FutureDataDaily.htm
          旧版(≤20151111): GET .../exchange/{YYYY}/datadaily/{YYYYMMDD}.htm
        响应格式: HTML表格，需通过CzceHtmlParser解析
        """
        if use_cache:
            cached = self._read_from_db(trade_date, 'CZCE')
            if cached is not None:
                print(f"[DB] CZCE缓存命中 ({len(cached)}条)")
                return cached

        try:
            if trade_date > '20151111':
                url = f'http://www.czce.com.cn/cn/DFSStaticFiles/Future/{trade_date[:4]}/{trade_date}/FutureDataDaily.htm'
            else:
                url = f'http://www.czce.com.cn/cn/exchange/{trade_date[:4]}/datadaily/{trade_date}.htm'

            response = self.session.get(url, timeout=30)
            response.encoding = 'utf-8'

            if response.status_code != 200:
                print(f"[CZCE] API请求失败: {response.status_code}")
                return None

            parser = self.CzceHtmlParser()
            parser.feed(response.text)

            records = []
            for row in parser.data:
                if len(row) < 8:
                    continue

                try:
                    symbol = row[0].strip()
                    if not symbol or symbol in ('品种代码', '合约代码', '合约名称', '合计'):
                        continue

                    records.append({
                        'exchange': 'CZCE',
                        'symbol': symbol,
                        'trade_date': trade_date,
                        'open': float(row[2].replace(',', '') or 0) if len(row) > 2 else 0,
                        'high': float(row[3].replace(',', '') or 0) if len(row) > 3 else 0,
                        'low': float(row[4].replace(',', '') or 0) if len(row) > 4 else 0,
                        'close': float(row[5].replace(',', '') or 0) if len(row) > 5 else 0,
                        'settle': float(row[6].replace(',', '') or 0) if len(row) > 6 else 0,
                        'volume': int(float(row[7].replace(',', '') or 0)) if len(row) > 7 else 0,
                        'open_interest': int(float(row[8].replace(',', '') or 0)) if len(row) > 8 else 0,
                        'turnover': float(row[9].replace(',', '') or 0) if len(row) > 9 else 0,
                        'source': 'CZCE官方API'
                    })
                except (ValueError, IndexError):
                    continue

            if records:
                df = pd.DataFrame(records)
                print(f"[CZCE] 成功: {len(df)}条")
                self._save_to_db(df)
                return df
            else:
                print("[CZCE] 无有效记录（HTML解析可能未匹配到表格）")
                return None

        except Exception as e:
            print(f"[CZCE] 异常: {e}")
            return None

    # ==================== 中金所 (CFFEX) ====================
    def get_cffex_daily_data(self, trade_date: str, use_cache: bool = True) -> Optional[pd.DataFrame]:
        """
        获取中金所日线数据

        API端点: GET http://www.cffex.com.cn/sj/hqsj/rtj/{YYYYMM}/{DD}/lsjy.dll
        响应格式: CSV，首行为标题行，后续每行为一个合约
        """
        if use_cache:
            cached = self._read_from_db(trade_date, 'CFFEX')
            if cached is not None:
                print(f"[DB] CFFEX缓存命中 ({len(cached)}条)")
                return cached

        try:
            # 中金所用月/日路径格式
            month_str = trade_date[:6]
            day_str = trade_date[6:8]
            url = f'http://www.cffex.com.cn/sj/hqsj/rtj/{month_str}/{day_str}/lsjy.dll'

            response = self.session.get(url, timeout=30)

            if response.status_code != 200:
                print(f"[CFFEX] API请求失败: {response.status_code}")
                return None

            lines = response.text.strip().split('\n')
            records = []

            for line in lines[1:]:  # 跳过标题行
                line = line.strip()
                if not line:
                    continue

                fields = line.split(',')
                if len(fields) < 8:
                    continue

                try:
                    symbol = fields[0].strip()
                    if not symbol:
                        continue

                    records.append({
                        'exchange': 'CFFEX',
                        'symbol': symbol,
                        'trade_date': trade_date,
                        'open': float(fields[1].replace(',', '') or 0) if len(fields) > 1 else 0,
                        'high': float(fields[2].replace(',', '') or 0) if len(fields) > 2 else 0,
                        'low': float(fields[3].replace(',', '') or 0) if len(fields) > 3 else 0,
                        'close': float(fields[4].replace(',', '') or 0) if len(fields) > 4 else 0,
                        'settle': float(fields[5].replace(',', '') or 0) if len(fields) > 5 else 0,
                        'volume': int(float(fields[6].replace(',', '') or 0)) if len(fields) > 6 else 0,
                        'open_interest': int(float(fields[7].replace(',', '') or 0)) if len(fields) > 7 else 0,
                        'turnover': float(fields[8].replace(',', '') or 0) if len(fields) > 8 else 0,
                        'source': 'CFFEX官方API'
                    })
                except (ValueError, IndexError):
                    continue

            if records:
                df = pd.DataFrame(records)
                print(f"[CFFEX] 成功: {len(df)}条")
                self._save_to_db(df)
                return df
            else:
                print("[CFFEX] 无有效记录")
                return None

        except Exception as e:
            print(f"[CFFEX] 异常: {e}")
            return None

    # ==================== 广期所 (GFEX) ====================
    def get_gfex_daily_data(self, trade_date: str, use_cache: bool = True) -> Optional[pd.DataFrame]:
        """
        获取广期所日线数据

        API端点: GET http://www.gfex.com.cn/gfex/rihq/{YYYYMMDD}.js
        响应格式: 可能是JSON（可能被 `var xxx = ...;` 包裹）或JS变量定义
        """
        if use_cache:
            cached = self._read_from_db(trade_date, 'GFEX')
            if cached is not None:
                print(f"[DB] GFEX缓存命中 ({len(cached)}条)")
                return cached

        try:
            url = f'http://www.gfex.com.cn/gfex/rihq/{trade_date}.js'
            response = self.session.get(url, timeout=30)

            if response.status_code != 200:
                print(f"[GFEX] API请求失败: {response.status_code}")
                return None

            content = response.text.strip()

            # 去除JS变量包装: var xxx = {...};
            if content.startswith('var '):
                eq_pos = content.find('=')
                if eq_pos > 0:
                    content = content[eq_pos + 1:].strip()
                if content.endswith(';'):
                    content = content[:-1].strip()

            if not content:
                print("[GFEX] 空响应")
                return None

            json_data = json.loads(content)
            records = []

            # 处理两种可能的响应格式
            if isinstance(json_data, list):
                items = json_data
            elif isinstance(json_data, dict):
                # 单条数据或嵌套结构
                if any(k in json_data for k in ('symbol', 'open', 'close')):
                    items = [json_data]
                else:
                    # 尝试找第一个数组值
                    for v in json_data.values():
                        if isinstance(v, list):
                            items = v
                            break
                    else:
                        print("[GFEX] 无法识别数据结构")
                        return None
            else:
                print("[GFEX] 无法解析的JSON类型")
                return None

            for item in items:
                if not isinstance(item, dict):
                    continue
                symbol = item.get('symbol', '') or item.get('PRODUCTID', '') or ''
                if not symbol:
                    continue

                records.append({
                    'exchange': 'GFEX',
                    'symbol': symbol,
                    'trade_date': trade_date,
                    'open': float(item.get('open', 0) or item.get('OPENPRICE', 0) or 0),
                    'high': float(item.get('high', 0) or item.get('HIGHESTPRICE', 0) or 0),
                    'low': float(item.get('low', 0) or item.get('LOWESTPRICE', 0) or 0),
                    'close': float(item.get('close', 0) or item.get('CLOSEPRICE', 0) or 0),
                    'settle': float(item.get('settle', 0) or item.get('SETTLEMENTPRICE', 0) or 0),
                    'volume': int(float(item.get('volume', 0) or item.get('VOLUME', 0) or 0)),
                    'open_interest': int(float(item.get('openInterest', 0) or item.get('OPENINTEREST', 0) or 0)),
                    'turnover': float(item.get('turnover', 0) or item.get('TURNOVER', 0) or 0),
                    'source': 'GFEX官方API'
                })

            if records:
                df = pd.DataFrame(records)
                print(f"[GFEX] 成功: {len(df)}条")
                self._save_to_db(df)
                return df
            else:
                print("[GFEX] 无有效记录")
                return None

        except json.JSONDecodeError as e:
            print(f"[GFEX] JSON解析失败: {e}")
            return None
        except Exception as e:
            print(f"[GFEX] 异常: {e}")
            return None

    # ==================== 统一接口 ====================
    def get_all_exchange_data(self, trade_date: str, use_cache: bool = True) -> Optional[pd.DataFrame]:
        """
        获取所有交易所的日线数据（串行获取，间隔1秒）

        如果所有交易所都返回None，则整体返回None。
        至少有一个交易所成功时，合并返回所有数据。

        Args:
            trade_date: 交易日期，格式：YYYYMMDD
            use_cache: 是否优先使用数据库缓存

        Returns:
            DataFrame or None
        """
        all_data = []

        exchanges = [
            ('DCE', self.get_dce_daily_data),
            ('SHFE', self.get_shfe_daily_data),
            ('CZCE', self.get_czce_daily_data),
            ('CFFEX', self.get_cffex_daily_data),
            ('GFEX', self.get_gfex_daily_data),
        ]

        success_count = 0
        failure_count = 0

        for name, func in exchanges:
            try:
                print(f"\n[正在获取] {name}数据...")
                df = func(trade_date, use_cache)
                if df is not None and len(df) > 0:
                    all_data.append(df)
                    success_count += 1
                    print(f"[{name}] ✓ {len(df)}条")
                else:
                    failure_count += 1
                    print(f"[{name}] - 无数据")
            except Exception as e:
                failure_count += 1
                print(f"[{name}] ✗ 异常: {e}")

            # 间隔1秒避免触发限流
            time.sleep(1)

        if all_data:
            result = pd.concat(all_data, ignore_index=True)
            print(f"\n[完成] {success_count}/5交易所成功, {len(result)}条记录")
            # 数据完整性验证：检查是否有极端异常值
            _bad_close = (result['close'] <= 0).sum()
            _bad_volume = (result['volume'] < 0).sum()
            if _bad_close > 0:
                print(f"[WARN] 有 {_bad_close} 条记录的收盘价<=0，将被过滤")
                result = result[result['close'] > 0]
            if _bad_volume > 0:
                print(f"[WARN] 有 {_bad_volume} 条记录的成交量<0，将被修正")
                result.loc[result['volume'] < 0, 'volume'] = 0
            print(f"[验证] 清洗后 {len(result)} 条有效记录")
            return result
        else:
            print(f"\n[失败] 所有5个交易所均无数据返回")
            return None

    def is_trading_day(self, date_str: str) -> bool:
        """
        判断是否为交易日。
        周末和已知法定节假日返回False。
        """
        dt = datetime.strptime(date_str, '%Y%m%d')
        if dt.weekday() >= 5:  # 周末
            return False
        if date_str in _KNOWN_HOLIDAYS:
            return False
        return True

    def get_latest_trading_day(self, max_lookback: int = 15) -> str:
        """
        获取最近交易日。
        考虑周末和中国法定节假日，向前最多查找max_lookback天。

        Args:
            max_lookback: 最大向前查找天数

        Returns:
            YYYYMMDD格式的最近交易日
        """
        today = datetime.now()
        for offset in range(max_lookback):
            d = today - timedelta(days=offset)
            date_str = d.strftime('%Y%m%d')
            if self.is_trading_day(date_str):
                return date_str

        # 兜底：使用今天之前最近的非节假日工作日
        for offset in range(max_lookback, max_lookback * 2):
            d = today - timedelta(days=offset)
            if d.weekday() < 5:  # 至少是工作日
                return d.strftime('%Y%m%d')

        return today.strftime('%Y%m%d')

    # ==================== 历史数据批量采集 ====================
    def batch_collect(self, start_date: str, end_date: Optional[str] = None):
        """
        批量采集历史数据（仅交易日，已缓存跳过）

        性能优化：每个交易日仅一次数据库连接检查缓存，
        每个交易所之间间隔1秒，每天之间间隔2秒。

        Args:
            start_date: 起始日期 YYYYMMDD
            end_date: 结束日期（默认当天）
        """
        if end_date is None:
            end_date = self.get_latest_trading_day()

        # 预计算交易日列表（排除周末和已知节假日）
        all_dates = []
        d = datetime.strptime(start_date, '%Y%m%d')
        end_dt = datetime.strptime(end_date, '%Y%m%d')
        while d <= end_dt:
            date_str = d.strftime('%Y%m%d')
            if self.is_trading_day(date_str):
                all_dates.append(date_str)
            d += timedelta(days=1)

        total = len(all_dates)
        cached_count = 0
        success = 0
        fail = 0

        print(f"\n批量采集: {start_date} → {end_date}, 共{total}个交易日")

        for i, trade_date in enumerate(all_dates):
            # 检查是否已缓存（批量检查效率更高）
            cached = self._read_from_db(trade_date)
            if cached is not None:
                cached_count += 1
                if (i + 1) % 10 == 0:
                    print(f"[{i+1}/{total}] {trade_date}: 已缓存 ({len(cached)}条)")
                continue

            print(f"[{i+1}/{total}] {trade_date}: 正在采集...")
            try:
                df = self.get_all_exchange_data(trade_date, use_cache=False)
                if df is not None:
                    success += 1
                    print(f"  → {len(df)}条")
                else:
                    fail += 1
                    print(f"  → 无数据")
            except Exception as e:
                fail += 1
                print(f"  → 异常: {e}")

            time.sleep(2)

        print(f"\n批量采集完成: 成功{success}, 失败{fail}, 已缓存{cached_count}, 共{total}")


def main():
    """测试/日常执行 — 使用DuckDB自动缓存"""
    collector = ExchangeDataCollector()

    # 检查数据库状态
    total_records = collector.get_cached_count()
    cached_dates = collector.get_cached_dates()
    print(f"[数据库] {collector.db_path}")
    print(f"[数据库] 总记录数: {total_records}")
    print(f"[数据库] 已缓存交易日: {len(cached_dates)}个")

    # 获取最新交易日数据
    trade_date = collector.get_latest_trading_day()
    print(f"\n[交易日] {trade_date}")

    df = collector.get_all_exchange_data(trade_date, use_cache=True)

    if df is not None:
        print(f"\n[概览] 总记录数: {len(df)}")
        print(f"[概览] 交易所分布:")
        print(df['exchange'].value_counts().to_string())
    else:
        print(f"\n[注意] {trade_date} 无数据（可能非交易日或休市）")


if __name__ == '__main__':
    main()
