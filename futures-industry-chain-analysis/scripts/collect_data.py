# -*- coding: utf-8 -*-
"""
商品期货数据采集脚本。
从 TqSdk（首选）或 通达信MCP（降级）获取实时行情 + 技术指标，
输出 market_data.json 供 run_pipeline.py 消费。

用法:
    python -m scripts.collect_data [--output-dir DIR] [--data-dir DIR] [--source SOURCE]

数据源优先级: tqsdk > tdx > akshare
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

# ============================================================
# 品种定义：代码、名称、交易所
# ============================================================
FUTURES_SYMBOLS: List[dict] = [
    # 黑色系
    {'pid': 'rb', 'name': '螺纹钢', 'exchange': 'SHFE', 'tdx_code': 'rb0', 'tdx_setcode': '8'},
    {'pid': 'hc', 'name': '热卷', 'exchange': 'SHFE', 'tdx_code': 'hc0', 'tdx_setcode': '8'},
    {'pid': 'i',  'name': '铁矿石', 'exchange': 'DCE',  'tdx_code': 'i0',  'tdx_setcode': '8'},
    {'pid': 'j',  'name': '焦炭', 'exchange': 'DCE',  'tdx_code': 'j0',  'tdx_setcode': '8'},
    {'pid': 'jm', 'name': '焦煤', 'exchange': 'DCE',  'tdx_code': 'jm0', 'tdx_setcode': '8'},
    {'pid': 'SF', 'name': '硅铁', 'exchange': 'CZCE', 'tdx_code': 'SF0', 'tdx_setcode': '8'},
    {'pid': 'SM', 'name': '锰硅', 'exchange': 'CZCE', 'tdx_code': 'SM0', 'tdx_setcode': '8'},
    # 能源链
    {'pid': 'sc', 'name': '原油', 'exchange': 'INE',  'tdx_code': 'sc0', 'tdx_setcode': '8'},
    {'pid': 'lu', 'name': '低硫燃油', 'exchange': 'INE',  'tdx_code': 'lu0', 'tdx_setcode': '8'},
    {'pid': 'fu', 'name': '燃料油', 'exchange': 'SHFE', 'tdx_code': 'fu0', 'tdx_setcode': '8'},
    {'pid': 'bu', 'name': '沥青', 'exchange': 'SHFE', 'tdx_code': 'bu0', 'tdx_setcode': '8'},
    {'pid': 'pg', 'name': 'LPG', 'exchange': 'DCE',  'tdx_code': 'pg0', 'tdx_setcode': '8'},
    # 聚酯链
    {'pid': 'PX', 'name': 'PX', 'exchange': 'CZCE', 'tdx_code': 'PX0', 'tdx_setcode': '8'},
    {'pid': 'TA', 'name': 'PTA', 'exchange': 'CZCE', 'tdx_code': 'TA0', 'tdx_setcode': '8'},
    {'pid': 'PF', 'name': '短纤', 'exchange': 'CZCE', 'tdx_code': 'PF0', 'tdx_setcode': '8'},
    {'pid': 'PR', 'name': '瓶片', 'exchange': 'CZCE', 'tdx_code': 'PR0', 'tdx_setcode': '8'},
    # 油化工
    {'pid': 'eg', 'name': '乙二醇', 'exchange': 'DCE',  'tdx_code': 'eg0', 'tdx_setcode': '8'},
    {'pid': 'eb', 'name': '苯乙烯', 'exchange': 'DCE',  'tdx_code': 'eb0', 'tdx_setcode': '8'},
    {'pid': 'v',  'name': 'PVC', 'exchange': 'DCE',  'tdx_code': 'v0',  'tdx_setcode': '8'},
    {'pid': 'pp', 'name': '聚丙烯', 'exchange': 'DCE',  'tdx_code': 'pp0', 'tdx_setcode': '8'},
    {'pid': 'l',  'name': '塑料', 'exchange': 'DCE',  'tdx_code': 'l0',  'tdx_setcode': '8'},
    # 煤化工
    {'pid': 'MA', 'name': '甲醇', 'exchange': 'CZCE', 'tdx_code': 'MA0', 'tdx_setcode': '8'},
    {'pid': 'SH', 'name': '烧碱', 'exchange': 'CZCE', 'tdx_code': 'SH0', 'tdx_setcode': '8'},
    # 有色
    {'pid': 'cu', 'name': '沪铜', 'exchange': 'SHFE', 'tdx_code': 'cu0', 'tdx_setcode': '8'},
    {'pid': 'al', 'name': '沪铝', 'exchange': 'SHFE', 'tdx_code': 'al0', 'tdx_setcode': '8'},
    {'pid': 'zn', 'name': '沪锌', 'exchange': 'SHFE', 'tdx_code': 'zn0', 'tdx_setcode': '8'},
    {'pid': 'pb', 'name': '沪铅', 'exchange': 'SHFE', 'tdx_code': 'pb0', 'tdx_setcode': '8'},
    {'pid': 'ni', 'name': '沪镍', 'exchange': 'SHFE', 'tdx_code': 'ni0', 'tdx_setcode': '8'},
    {'pid': 'sn', 'name': '沪锡', 'exchange': 'SHFE', 'tdx_code': 'sn0', 'tdx_setcode': '8'},
    {'pid': 'ao', 'name': '氧化铝', 'exchange': 'SHFE', 'tdx_code': 'ao0', 'tdx_setcode': '8'},
    {'pid': 'SS', 'name': '不锈钢', 'exchange': 'SHFE', 'tdx_code': 'SS0', 'tdx_setcode': '8'},
    # 贵金属
    {'pid': 'au', 'name': '沪金', 'exchange': 'SHFE', 'tdx_code': 'au0', 'tdx_setcode': '8'},
    {'pid': 'ag', 'name': '沪银', 'exchange': 'SHFE', 'tdx_code': 'ag0', 'tdx_setcode': '8'},
    # 油脂油料
    {'pid': 'a',  'name': '豆一', 'exchange': 'DCE',  'tdx_code': 'a0',  'tdx_setcode': '8'},
    {'pid': 'b',  'name': '豆二', 'exchange': 'DCE',  'tdx_code': 'b0',  'tdx_setcode': '8'},
    {'pid': 'm',  'name': '豆粕', 'exchange': 'DCE',  'tdx_code': 'm0',  'tdx_setcode': '8'},
    {'pid': 'y',  'name': '豆油', 'exchange': 'DCE',  'tdx_code': 'y0',  'tdx_setcode': '8'},
    {'pid': 'p',  'name': '棕榈油', 'exchange': 'DCE',  'tdx_code': 'p0',  'tdx_setcode': '8'},
    {'pid': 'OI', 'name': '菜油', 'exchange': 'CZCE', 'tdx_code': 'OI0', 'tdx_setcode': '8'},
    {'pid': 'RM', 'name': '菜粕', 'exchange': 'CZCE', 'tdx_code': 'RM0', 'tdx_setcode': '8'},
    {'pid': 'PK', 'name': '花生', 'exchange': 'CZCE', 'tdx_code': 'PK0', 'tdx_setcode': '8'},
    # 谷物软商品
    {'pid': 'c',  'name': '玉米', 'exchange': 'DCE',  'tdx_code': 'c0',  'tdx_setcode': '8'},
    {'pid': 'cs', 'name': '玉米淀粉', 'exchange': 'DCE',  'tdx_code': 'cs0', 'tdx_setcode': '8'},
    {'pid': 'SR', 'name': '白糖', 'exchange': 'CZCE', 'tdx_code': 'SR0', 'tdx_setcode': '8'},
    {'pid': 'CF', 'name': '棉花', 'exchange': 'CZCE', 'tdx_code': 'CF0', 'tdx_setcode': '8'},
    {'pid': 'jd', 'name': '鸡蛋', 'exchange': 'DCE',  'tdx_code': 'jd0', 'tdx_setcode': '8'},
    {'pid': 'lh', 'name': '生猪', 'exchange': 'DCE',  'tdx_code': 'lh0', 'tdx_setcode': '8'},
    {'pid': 'AP', 'name': '苹果', 'exchange': 'CZCE', 'tdx_code': 'AP0', 'tdx_setcode': '8'},
    {'pid': 'CJ', 'name': '红枣', 'exchange': 'CZCE', 'tdx_code': 'CJ0', 'tdx_setcode': '8'},
    # 建材
    {'pid': 'FG', 'name': '玻璃', 'exchange': 'CZCE', 'tdx_code': 'FG0', 'tdx_setcode': '8'},
    {'pid': 'SA', 'name': '纯碱', 'exchange': 'CZCE', 'tdx_code': 'SA0', 'tdx_setcode': '8'},
    {'pid': 'UR', 'name': '尿素', 'exchange': 'CZCE', 'tdx_code': 'UR0', 'tdx_setcode': '8'},
    # 橡胶
    {'pid': 'ru', 'name': '橡胶', 'exchange': 'SHFE', 'tdx_code': 'ru0', 'tdx_setcode': '8'},
    {'pid': 'nr', 'name': '20号胶', 'exchange': 'INE',  'tdx_code': 'nr0', 'tdx_setcode': '8'},
    {'pid': 'br', 'name': 'BR橡胶', 'exchange': 'SHFE', 'tdx_code': 'br0', 'tdx_setcode': '8'},
    # 纸浆造纸
    {'pid': 'sp', 'name': '纸浆', 'exchange': 'SHFE', 'tdx_code': 'sp0', 'tdx_setcode': '8'},
    {'pid': 'op', 'name': '双胶纸', 'exchange': 'SHFE', 'tdx_code': 'op0', 'tdx_setcode': '8'},
    # 新增品种（持仓量 > 10000）
    {'pid': 'lc', 'name': '碳酸锂', 'exchange': 'GFEX', 'tdx_code': 'lc0', 'tdx_setcode': '8'},
    {'pid': 'si', 'name': '工业硅', 'exchange': 'GFEX', 'tdx_code': 'si0', 'tdx_setcode': '8'},
    {'pid': 'ps', 'name': '多晶硅', 'exchange': 'GFEX', 'tdx_code': 'ps0', 'tdx_setcode': '8'},
    {'pid': 'ec', 'name': '集运指数欧线', 'exchange': 'INE', 'tdx_code': 'ec0', 'tdx_setcode': '8'},
    {'pid': 'rr', 'name': '粳米', 'exchange': 'DCE', 'tdx_code': 'rr0', 'tdx_setcode': '8'},
    {'pid': 'PL', 'name': '丙烯', 'exchange': 'CZCE', 'tdx_code': 'PL0', 'tdx_setcode': '8'},
    {'pid': 'ad', 'name': '铸造铝合金', 'exchange': 'SHFE', 'tdx_code': 'ad0', 'tdx_setcode': '8'},
    {'pid': 'CY', 'name': '棉纱', 'exchange': 'CZCE', 'tdx_code': 'CY0', 'tdx_setcode': '8'},
    {'pid': 'bz', 'name': '纯苯', 'exchange': 'DCE', 'tdx_code': 'bz0', 'tdx_setcode': '8'},
    {'pid': 'pt', 'name': '铂', 'exchange': 'SHFE', 'tdx_code': 'pt0', 'tdx_setcode': '8'},
]


# ============================================================
# 技术指标计算（纯 Python，不依赖 TqSdk）
# ============================================================

def _calc_ma(closes: List[float], period: int) -> Optional[float]:
    """计算简单移动平均线。"""
    if len(closes) < period:
        return None
    return round(sum(closes[-period:]) / period, 4)


def _calc_ema(closes: List[float], period: int) -> List[float]:
    """计算指数移动平均线。"""
    if not closes:
        return []
    emas = [closes[0]]
    k = 2.0 / (period + 1)
    for i in range(1, len(closes)):
        emas.append(closes[i] * k + emas[-1] * (1 - k))
    return emas


def _calc_macd(closes: List[float], fast=12, slow=26, signal=9) -> Optional[dict]:
    """计算MACD (DIF, DEA, Histogram)。"""
    if len(closes) < slow + signal:
        return None
    ema_fast = _calc_ema(closes, fast)
    ema_slow = _calc_ema(closes, slow)
    dif = [ema_fast[i] - ema_slow[i] for i in range(len(closes))]
    dea = _calc_ema(dif, signal)
    hist = [(dif[i] - dea[i]) * 2 for i in range(len(closes))]
    return {
        'DIF': round(dif[-1], 4),
        'DEA': round(dea[-1], 4),
        'HIST': round(hist[-1], 4),
    }


def _calc_rsi(closes: List[float], period=14) -> Optional[float]:
    """计算RSI。"""
    if len(closes) < period + 1:
        return None
    gains, losses = [], []
    for i in range(1, len(closes)):
        diff = closes[i] - closes[i - 1]
        gains.append(max(diff, 0))
        losses.append(max(-diff, 0))
    if len(gains) < period:
        return None
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return round(100 - 100 / (1 + rs), 2)


def _calc_atr(highs: List[float], lows: List[float], closes: List[float], period=14) -> Optional[float]:
    """计算ATR。"""
    if len(closes) < period + 1:
        return None
    trs = []
    for i in range(1, len(closes)):
        tr = max(
            highs[i] - lows[i],
            abs(highs[i] - closes[i - 1]),
            abs(lows[i] - closes[i - 1])
        )
        trs.append(tr)
    if len(trs) < period:
        return None
    return round(sum(trs[-period:]) / period, 4)


def _calc_dmi(highs: List[float], lows: List[float], closes: List[float],
              period=14, smooth=6) -> Optional[dict]:
    """计算DMI (+DI, -DI, ADX)。"""
    n = period + smooth
    if len(closes) < n + 1:
        return None
    # 计算 TR, +DM, -DM
    trs, pdms, mdms = [], [], []
    for i in range(1, len(closes)):
        tr = max(highs[i] - lows[i], abs(highs[i] - closes[i-1]), abs(lows[i] - closes[i-1]))
        pdm = max(highs[i] - highs[i-1], 0) if highs[i] - highs[i-1] > lows[i-1] - lows[i] else 0
        mdm = max(lows[i-1] - lows[i], 0) if lows[i-1] - lows[i] > highs[i] - highs[i-1] else 0
        trs.append(tr)
        pdms.append(pdm)
        mdms.append(mdm)

    # Wilder 平滑
    def wilder_smooth(data, p):
        result = [sum(data[:p])]
        for i in range(p, len(data)):
            result.append(result[-1] - result[-1] / p + data[i])
        return result

    if len(trs) < period:
        return None

    sm_tr = wilder_smooth(trs, period)
    sm_pdm = wilder_smooth(pdms, period)
    sm_mdm = wilder_smooth(mdms, period)

    if not sm_tr or sm_tr[-1] == 0:
        return None

    pdi = (sm_pdm[-1] / sm_tr[-1]) * 100
    mdi = (sm_mdm[-1] / sm_tr[-1]) * 100
    dx = abs(pdi - mdi) / (pdi + mdi) * 100 if (pdi + mdi) > 0 else 0

    return {
        'PDI': round(pdi, 2),
        'MDI': round(mdi, 2),
        'ADX': round(dx, 2),  # 简化版，未做 ADX 的 Wilder 平滑
    }


def _calc_obv(closes: List[float], volumes: List[float]) -> Optional[dict]:
    """计算OBV及其20日均线。"""
    if len(closes) < 2 or len(volumes) < 2:
        return None
    obv = [0]
    for i in range(1, len(closes)):
        if closes[i] > closes[i-1]:
            obv.append(obv[-1] + volumes[i])
        elif closes[i] < closes[i-1]:
            obv.append(obv[-1] - volumes[i])
        else:
            obv.append(obv[-1])

    obv_ma20 = None
    if len(obv) >= 20:
        obv_ma20 = round(sum(obv[-20:]) / 20, 2)

    return {
        'OBV': round(obv[-1], 2),
        'OBV_MA20': obv_ma20,
    }


def compute_indicators_from_klines(klines: List[dict]) -> dict:
    """从K线数据计算全部技术指标。klines为 [{open, high, low, close, volume}, ...]"""
    if not klines or len(klines) < 30:
        return {}

    closes = [k['close'] for k in klines]
    highs = [k['high'] for k in klines]
    lows = [k['low'] for k in klines]
    volumes = [k['volume'] for k in klines]

    tech = {}

    # MA（含长周期MA40/MA60用于趋势结构确认）
    tech['MA5'] = _calc_ma(closes, 5)
    tech['MA10'] = _calc_ma(closes, 10)
    tech['MA20'] = _calc_ma(closes, 20)
    tech['MA40'] = _calc_ma(closes, 40)
    tech['MA60'] = _calc_ma(closes, 60)

    # MACD
    macd = _calc_macd(closes)
    if macd:
        tech['MACD_DIF'] = macd['DIF']
        tech['MACD_DEA'] = macd['DEA']
        tech['MACD_HIST'] = macd['HIST']

    # RSI
    tech['RSI14'] = _calc_rsi(closes)

    # ATR
    tech['ATR14'] = _calc_atr(highs, lows, closes)

    # DMI
    dmi = _calc_dmi(highs, lows, closes)
    if dmi:
        tech['DMI_PDI'] = dmi['PDI']
        tech['DMI_MDI'] = dmi['MDI']
        tech['ADX'] = dmi['ADX']

    # OBV
    obv = _calc_obv(closes, volumes)
    if obv:
        tech['OBV'] = obv['OBV']
        tech['OBV_MA20'] = obv['OBV_MA20']

    # 近高近低
    if len(closes) >= 20:
        tech['recent_high'] = round(max(highs[-20:]), 2)
        tech['recent_low'] = round(min(lows[-20:]), 2)

    return tech


# ============================================================
# 数据源：TqSdk
# ============================================================

def fetch_from_tqsdk(symbols: List[dict]) -> List[dict]:
    """通过 TqSdk 获取实时行情 + K线 + 技术指标。"""
    try:
        from tqsdk import TqApi, TqAuth
        from tqsdk.ta import MA, MACD, RSI, DMI, ATR
    except ImportError:
        print("[ERROR] TqSdk 未安装，请 pip install tqsdk")
        return []

    tq_user = os.environ.get('TQSDK_USERNAME') or os.environ.get('TQ_USER')
    tq_password = os.environ.get('TQSDK_PASSWORD') or os.environ.get('TQ_PASSWORD')
    if not tq_user or not tq_password:
        print("[ERROR] TQSDK_USERNAME/TQSDK_PASSWORD 或 TQ_USER/TQ_PASSWORD 环境变量未设置")
        return []

    print(f"[TqSdk] 连接中... 用户: {tq_user[:3]}***")
    auth = TqAuth(tq_user, tq_password)

    try:
        api = TqApi(auth=auth)
    except Exception as e:
        print(f"[ERROR] TqSdk 连接失败: {e}")
        return []

    results = []
    # 批量订阅
    quotes_map = {}
    klines_map = {}

    for sym in symbols:
        pid = sym['pid']
        exchange = sym['exchange']
        # 主力连续合约: KQ.m@EXCHANGE.product
        tq_symbol = f"KQ.m@{exchange}.{pid}"
        try:
            quote = api.get_quote(tq_symbol)
            klines = api.get_kline_serial(tq_symbol, 24 * 3600, 80)  # 80根日K
            quotes_map[pid] = quote
            klines_map[pid] = klines
        except Exception as e:
            print(f"  [WARN] 订阅 {tq_symbol} 失败: {e}")

    # 等待数据到达
    try:
        deadline = time.time() + 15
        while time.time() < deadline:
            api.wait_update(deadline=time.time() + 1)
            if all(api.is_changing(klines_map[p], "close") or True for p in klines_map):
                break
    except Exception:
        pass

    # 提取数据
    for sym in symbols:
        pid = sym['pid']
        if pid not in quotes_map:
            print(f"  [SKIP] {pid} 无行情数据")
            continue

        q = quotes_map[pid]
        kl = klines_map.get(pid)

        last_price = float(q.last_price) if q.last_price else 0
        if last_price <= 0:
            print(f"  [SKIP] {pid} 价格为0")
            continue

        # 从K线计算技术指标
        tech = {}
        if kl is not None and len(kl) > 0:
            closes = kl['close'].tolist()
            highs = kl['highest'].tolist()
            lows = kl['lowest'].tolist()
            volumes = kl['volume'].tolist()
            # 过滤 NaN
            valid = [(c, h, l, v) for c, h, l, v in zip(closes, highs, lows, volumes)
                     if c == c and h == h and l == l and v == v]  # NaN != NaN
            if len(valid) >= 30:
                vc, vh, vl, vv = zip(*valid)
                kline_dicts = [{'close': c, 'high': h, 'low': l, 'volume': v}
                               for c, h, l, v in zip(vc, vh, vl, vv)]
                tech = compute_indicators_from_klines(kline_dicts)

        open_interest = int(q.open_interest) if hasattr(q, 'open_interest') and q.open_interest else 0

        # 趋势评分
        from .indicators import calculate_trend_score
        sym_data = {'last_price': last_price, 'open_interest': open_interest}
        trend = calculate_trend_score(tech, sym_data, chain_name='')

        results.append({
            'product_id': pid,
            'product_name': sym['name'],
            'last_price': last_price,
            'open_interest': open_interest,
            'change_pct': round((last_price / float(q.pre_close) - 1) * 100, 2) if hasattr(q, 'pre_close') and q.pre_close else 0,
            'tech': tech,
            'trend': trend,
        })
        print(f"  [OK] {pid} ({sym['name']}): {last_price}, 得分={trend.get('score', 0)}")

    api.close()
    return results


# ============================================================
# 数据源：通达信 MCP (tdx-connector)
# ============================================================

def _tdx_fetch_kline(tdx_code: str, setcode: str = '8', want_num: int = 80) -> List[dict]:
    """通过通达信获取日K线数据。返回 [{open, high, low, close, volume}, ...]"""
    import subprocess
    import json as _json

    # 使用 Python 调用 tdx-connector MCP 是不现实的，这里用 subprocess 调用
    # 实际上需要通过 MCP 协议。降级方案：直接用 AKShare
    return []


def fetch_from_tdx(symbols: List[dict]) -> List[dict]:
    """通过通达信获取数据（降级）。实际使用时通过 MCP 工具调用。"""
    # 此函数作为占位，实际在 agent 模式下通过 mcp__tdx-connector 工具调用
    print("[TDX] 通达信数据源需要通过 MCP 工具调用，请使用 agent 模式")
    return []


# ============================================================
# 数据源：AKShare
# ============================================================

def fetch_from_akshare(symbols: List[dict]) -> List[dict]:
    """通过 AKShare 获取期货数据（使用 futures_main_sina 接口）。"""
    try:
        import akshare as ak
    except ImportError:
        print("[ERROR] AKShare 未安装，请 pip install akshare")
        return []

    print("[AKShare] 获取期货行情（futures_main_sina）...")
    results = []

    # 取120天K线用于技术指标计算
    end_date = datetime.now().strftime('%Y%m%d')
    start_date = (datetime.now() - timedelta(days=150)).strftime('%Y%m%d')

    for sym in symbols:
        pid = sym['pid']
        # AKShare 主力连续合约格式: {pid小写}0，如 rb0, i0, sc0, sf0, ma0
        ak_symbol = pid.lower() + '0'

        try:
            df = ak.futures_main_sina(symbol=ak_symbol, start_date=start_date, end_date=end_date)
            if df is None or df.empty:
                print(f"  [SKIP] {pid} ({ak_symbol}) 无数据")
                continue

            # 提取最新行情
            last = df.iloc[-1]
            prev = df.iloc[-2] if len(df) > 1 else last
            last_price = float(last['收盘价'])
            prev_close = float(prev['收盘价'])
            change_pct = round((last_price / prev_close - 1) * 100, 2) if prev_close > 0 else 0
            open_interest = int(last.get('持仓量', 0) or 0)

            if last_price <= 0:
                print(f"  [SKIP] {pid} 价格为0")
                continue

            # 从K线计算技术指标
            klines = []
            for _, row in df.iterrows():
                klines.append({
                    'open': float(row.get('开盘价', 0) or 0),
                    'high': float(row.get('最高价', 0) or 0),
                    'low': float(row.get('最低价', 0) or 0),
                    'close': float(row.get('收盘价', 0) or 0),
                    'volume': int(row.get('成交量', 0) or 0),
                })

            tech = compute_indicators_from_klines(klines)

            # 趋势评分
            from .indicators import calculate_trend_score
            sym_data = {'last_price': last_price, 'open_interest': open_interest}
            trend = calculate_trend_score(tech, sym_data, chain_name='')

            results.append({
                'product_id': pid,
                'product_name': sym['name'],
                'last_price': last_price,
                'open_interest': open_interest,
                'change_pct': change_pct,
                'tech': tech,
                'trend': trend,
            })
            print(f"  [OK] {pid} ({sym['name']}): {last_price}, 得分={trend.get('score', 0)}")

            # AKShare 有频率限制，短暂延时
            time.sleep(0.3)

        except Exception as e:
            print(f"  [WARN] {pid} ({ak_symbol}) 获取失败: {e}")

    return results


# ============================================================
# 数据源：交易所官方API（最权威，无爬虫合规风险）
# ============================================================

def fetch_from_exchange_official(symbols: List[dict]) -> List[dict]:
    """
    通过交易所官方API获取期货数据（最权威数据源）。
    
    支持交易所：
    - 大商所 (DCE)
    - 上期所 (SHFE)
    - 郑商所 (CZCE)
    - 中金所 (CFFEX)
    - 广期所 (GFEX)
    
    数据源优先级：交易所官方API > AKShare > TqSdk
    """
    try:
        # 导入交易所数据采集模块
        import sys
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from exchange_data_collector import ExchangeDataCollector
    except ImportError as e:
        print(f"[ERROR] 交易所数据采集模块导入失败: {e}")
        return []
    
    print("[交易所官方API] 开始获取数据...")
    
    collector = ExchangeDataCollector()
    
    # 获取最近交易日
    trade_date = collector.get_latest_trading_day()
    print(f"  交易日: {trade_date}")
    
    # 获取所有交易所数据
    exchange_df = collector.get_all_exchange_data(trade_date)
    
    if exchange_df is None or len(exchange_df) == 0:
        print("[交易所官方API] 数据获取失败")
        return []
    
    print(f"[交易所官方API] 获取到 {len(exchange_df)} 条记录")
    
    # 将交易所数据转换为内部格式
    results = []
    
    for sym in symbols:
        pid = sym['pid']
        exchange = sym['exchange']
        
        # 从交易所数据中查找匹配的品种
        # 匹配规则：交易所 + 品种代码
        matched = exchange_df[
            (exchange_df['exchange'] == exchange) & 
            (exchange_df['symbol'].str.contains(pid, case=False, na=False))
        ]
        
        if matched.empty:
            # 尝试模糊匹配
            matched = exchange_df[
                exchange_df['symbol'].str.contains(pid.lower(), case=False, na=False)
            ]
        
        if matched.empty:
            print(f"  [SKIP] {pid} ({sym['name']}) 未找到交易所数据")
            continue
        
        # 取最新一条数据
        latest = matched.iloc[-1]
        
        last_price = float(latest.get('close', 0))
        if last_price <= 0:
            print(f"  [SKIP] {pid} 价格为0")
            continue
        
        open_interest = int(latest.get('open_interest', 0))
        
        # 构建K线数据（如果有历史数据）
        klines = []
        if len(matched) > 1:
            for _, row in matched.iterrows():
                klines.append({
                    'open': float(row.get('open', 0)),
                    'high': float(row.get('high', 0)),
                    'low': float(row.get('low', 0)),
                    'close': float(row.get('close', 0)),
                    'volume': int(row.get('volume', 0)),
                })
        
        # 计算技术指标
        tech = {}
        if len(klines) >= 30:
            tech = compute_indicators_from_klines(klines)
        
        # 趋势评分
        from .indicators import calculate_trend_score
        sym_data = {'last_price': last_price, 'open_interest': open_interest}
        trend = calculate_trend_score(tech, sym_data, chain_name='')
        
        # 计算涨跌幅
        change_pct = 0
        if len(matched) > 1:
            prev_close = float(matched.iloc[-2].get('close', 0))
            if prev_close > 0:
                change_pct = round((last_price / prev_close - 1) * 100, 2)
        
        results.append({
            'product_id': pid,
            'product_name': sym['name'],
            'last_price': last_price,
            'open_interest': open_interest,
            'change_pct': change_pct,
            'tech': tech,
            'trend': trend,
            'data_source': '交易所官方API',
            'exchange': exchange,
            'trade_date': trade_date,
        })
        print(f"  [OK] {pid} ({sym['name']}): {last_price}, 得分={trend.get('score', 0)}")
    
    return results


# ============================================================
# 数据源组合：交易所官方API → TqSdk → AKShare
# ============================================================

def collect_all_data(source: str = 'auto', min_oi: int = 10000) -> dict:
    """采集所有品种数据。返回 market_data.json 格式的 dict。"""
    print(f"\n{'='*60}")
    print(f"商品期货数据采集 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"数据源: {source} | 最低持仓量: {min_oi}")
    print(f"{'='*60}\n")

    symbols = None
    data_source = 'none'

    # 数据源优先级：交易所官方API → TqSdk → AKShare
    if source in ('auto', 'exchange'):
        print("[1] 尝试 交易所官方API...")
        symbols = fetch_from_exchange_official(FUTURES_SYMBOLS)
        if symbols:
            data_source = 'exchange_official'
    
    if not symbols and source in ('auto', 'tqsdk'):
        print("[2] 尝试 TqSdk...")
        symbols = fetch_from_tqsdk(FUTURES_SYMBOLS)
        if symbols:
            data_source = 'tqsdk'

    if not symbols and source in ('auto', 'akshare'):
        print("[3] 尝试 AKShare...")
        symbols = fetch_from_akshare(FUTURES_SYMBOLS)
        if symbols:
            data_source = 'akshare'

    if not symbols:
        print("[ERROR] 所有数据源均失败，无法获取数据")
        return {'symbols': [], 'meta': {'source': 'none', 'timestamp': datetime.now().isoformat()}}

    # 过滤持仓量 + 数据有效性验证
    valid_symbols = []
    rejected_reasons = {'zero_price': 0, 'stale_data': 0, 'low_oi': 0}
    
    for s in symbols:
        price = s.get('last_price', 0)
        oi = s.get('open_interest', 0)
        
        # 价格必须为正数
        if price <= 0:
            rejected_reasons['zero_price'] += 1
            continue
        
        # 持仓量过滤
        if min_oi > 0 and oi < min_oi:
            rejected_reasons['low_oi'] += 1
            continue
        
        # 添加数据来源和时效性标记
        s['source'] = data_source
        s['timestamp'] = datetime.now().isoformat()
        valid_symbols.append(s)
    
    if rejected_reasons['zero_price'] > 0:
        print(f"[VALIDATION] 剔除零价格品种: {rejected_reasons['zero_price']} 个")
    if rejected_reasons['low_oi'] > 0:
        print(f"[VALIDATION] 剔除低持仓品种: {rejected_reasons['low_oi']} 个")
    
    symbols = valid_symbols
    if not symbols:
        print("[VALIDATION] 所有品种均被剔除，返回空数据")

    print(f"\n采集完成: {len(symbols)} 个品种, 数据源: {data_source}")

    return {
        'symbols': symbols,
        'meta': {
            'source': data_source,
            'timestamp': datetime.now().isoformat(),
            'count': len(symbols),
            'min_open_interest': min_oi,
        },
    }


# ============================================================
# 主入口
# ============================================================

def main():
    parser = argparse.ArgumentParser(description='商品期货数据采集')
    parser.add_argument('--output-dir', default=None, help='输出目录（默认: data_dir 参数）')
    parser.add_argument('--data-dir', default=None, help='数据目录（默认: 技能目录下的 data/）')
    parser.add_argument('--source', default='auto', choices=['auto', 'exchange', 'tqsdk', 'akshare'],
                        help='数据源（默认: auto 自动降级）')
    parser.add_argument('--min-oi', type=int, default=10000, help='最低持仓量过滤（默认: 10000）')
    args = parser.parse_args()

    # 确定输出目录
    skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = args.data_dir or os.path.join(skill_dir, 'data')
    output_dir = args.output_dir or data_dir

    os.makedirs(output_dir, exist_ok=True)

    # 采集数据
    market_data = collect_all_data(source=args.source, min_oi=args.min_oi)

    # 保存
    output_path = os.path.join(output_dir, 'market_data.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(market_data, f, ensure_ascii=False, indent=2)

    print(f"\n数据已保存: {output_path}")
    print(f"品种数: {market_data['meta']['count']}")
    print(f"数据源: {market_data['meta']['source']}")

    return market_data


if __name__ == '__main__':
    main()
