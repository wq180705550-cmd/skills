# -*- coding: utf-8 -*-
"""技术指标计算与趋势评分。"""

from typing import Optional


def safe_float(val) -> Optional[float]:
    """安全转换为float。"""
    try:
        import pandas as pd
        if isinstance(val, pd.Series):
            val = val.iloc[-1]
        if pd.isna(val):
            return None
        return float(val)
    except Exception:
        return None


def identify_market_state(tech_data: dict, sym_data: dict) -> tuple:
    """识别市场状态。返回 (market_state, trend_score)。"""
    from .config import MARKET_STATE_SYSTEM

    ma5 = tech_data.get('MA5')
    ma10 = tech_data.get('MA10')
    ma20 = tech_data.get('MA20')
    ma40 = tech_data.get('MA40')
    ma60 = tech_data.get('MA60')
    atr = tech_data.get('ATR14')
    last_price = sym_data.get('last_price')

    trend_score = 0
    # 多层级MA排列判断（短中期MA5>MA10>MA20，中长期MA20>MA40>MA60）
    if ma5 and ma10 and ma20:
        short_bull = ma5 > ma10 > ma20
        short_bear = ma5 < ma10 < ma20
        long_bull = (ma20 > ma40 > ma60) if (ma40 and ma60) else short_bull
        long_bear = (ma20 < ma40 < ma60) if (ma40 and ma60) else short_bear

        # 紧密度检测：MA5-MA20间距<0.5% → 震荡，排列信号不可靠
        ma_spread = abs(ma5 - ma20) / ma20 if ma20 else 0
        is_tight = ma_spread < 0.005

        if short_bull and long_bull and not is_tight:
            trend_score = 30  # 完全多头排列
        elif short_bull and not is_tight:
            trend_score = 15  # 仅短周期多头（长周期未配合）
        elif short_bear and long_bear and not is_tight:
            trend_score = -30  # 完全空头排列
        elif short_bear and not is_tight:
            trend_score = -15  # 仅短周期空头

    volatility = 0
    if atr and last_price:
        volatility = atr / last_price * 100

    if abs(trend_score) >= MARKET_STATE_SYSTEM['trend_threshold']:
        if volatility >= MARKET_STATE_SYSTEM['volatile_threshold']:
            return 'volatile', trend_score
        return 'trending', trend_score
    elif abs(trend_score) <= MARKET_STATE_SYSTEM['range_threshold']:
        return 'ranging', trend_score
    return 'transitional', trend_score


def calculate_trend_score(tech: dict, sym: dict, chain_name: str = '') -> dict:
    """计算趋势评分（自适应权重版）。返回 {'score': int, 'trend': str, 'reasons': list}。"""
    from .config import get_adaptive_weights, get_product_type

    market_state, _ = identify_market_state(tech, sym)
    product_type = get_product_type(chain_name) if chain_name else 'industrial'
    weights = get_adaptive_weights(product_type, market_state)

    score = 0
    reasons = []

    ma5, ma10, ma20 = tech.get('MA5'), tech.get('MA10'), tech.get('MA20')
    ma40, ma60 = tech.get('MA40'), tech.get('MA60')
    macd_dif = tech.get('MACD_DIF')
    macd_dea = tech.get('MACD_DEA')
    rsi = tech.get('RSI14')
    pdi, mdi = tech.get('DMI_PDI'), tech.get('DMI_MDI')
    atr = tech.get('ATR14')
    obv = tech.get('OBV')
    obv_ma20 = tech.get('OBV_MA20')

    # MA多层级排列（逐级验证，非全有全无）
    last_price = sym.get('last_price')
    if ma5 and ma10 and ma20:
        w = weights.get('MA', 30)

        # === 层级1: 短周期排列 (MA5/MA10/MA20) ===
        short_bull = ma5 > ma10 > ma20
        short_bear = ma5 < ma10 < ma20

        # === 层级2: 长周期排列 (MA20/MA40/MA60) ===
        long_bull = (ma20 > ma40 > ma60) if (ma40 and ma60) else short_bull
        long_bear = (ma20 < ma40 < ma60) if (ma40 and ma60) else short_bear

        # === 紧密度检测 ===
        ma_spread = abs(ma5 - ma20) / ma20 if ma20 else 0
        is_tight_ma = ma_spread < 0.005  # MA间距 < 0.5% → 震荡

        # === 价格相对于MA20的位置 ===
        price_above = last_price and last_price >= ma20
        price_below = last_price and last_price <= ma20

        # === 综合评分 ===
        if is_tight_ma:
            # 均线紧密纠缠 → 震荡，大幅减分
            if short_bull and price_above:
                score += w * 0.10
                reasons.append(f'MA短多但紧密震荡(spread={ma_spread:.3f},{w*0.10:.0f})')
            elif short_bear and price_below:
                score -= w * 0.10
                reasons.append(f'MA短空但紧密震荡(spread={ma_spread:.3f},{-w*0.10:.0f})')
        elif short_bull and long_bull and price_above:
            # 完全多头排列（短+长共振） + 价格在MA20上 = 最强
            score += w
            reasons.append(f'MA完全多头排列(短+长共振,{w:.0f})')
        elif short_bull and price_above:
            # 仅短周期多头（长周期未配合）= 弱多头
            score += w * 0.5
            reasons.append(f'MA短多但长周期未共振({w*0.5:.0f})')
        elif short_bull and not price_above:
            # MA排列多头但价格跌破MA20 → 排列已破坏
            score += w * 0.2
            reasons.append(f'MA排列多头但价格跌破MA20({w*0.2:.0f})')
        elif short_bear and long_bear and price_below:
            # 完全空头排列 + 价格在MA20下 = 最强
            score -= w
            reasons.append(f'MA完全空头排列(短+长共振,{-w:.0f})')
        elif short_bear and price_below:
            score -= w * 0.5
            reasons.append(f'MA短空但长周期未共振({-w*0.5:.0f})')
        elif short_bear and not price_below:
            score -= w * 0.2
            reasons.append(f'MA排列空头但价格突破MA20({-w*0.2:.0f})')

    # MACD（区分零轴上下 + 金叉/死叉，非纯二元判断）
    if macd_dif is not None:
        w = weights.get('MACD', 20)
        if macd_dif > 0:
            # 零轴上方
            if macd_dea is not None and macd_dif > macd_dea:
                # 零轴上 + 金叉（DIF > DEA）→ 最强多头
                score += w
                reasons.append(f'MACD零轴上金叉({w:.0f})')
            elif macd_dea is not None:
                # 零轴上 + 死叉 → 多头减弱
                score += w * 0.5
                reasons.append(f'MACD零轴上死叉(DIF↓,{w*0.5:.0f})')
            else:
                score += w * 0.7  # 无DEA时保守
                reasons.append(f'MACD零轴上({w*0.7:.0f})')
        else:
            # 零轴下方
            if macd_dea is not None and macd_dif > macd_dea:
                # 零轴下 + 金叉（DIF上穿DEA）→ 弱势反弹，减分减弱
                score -= w * 0.4
                reasons.append(f'MACD零轴下金叉(弱势反弹,{-w*0.4:.0f})')
            elif macd_dea is not None:
                # 零轴下 + 死叉 → 最强空头
                score -= w
                reasons.append(f'MACD零轴下死叉({-w:.0f})')
            else:
                score -= w * 0.7
                reasons.append(f'MACD零轴下({-w*0.7:.0f})')

    # RSI
    if rsi is not None:
        w = weights.get('RSI', 10)
        if rsi < 30:
            score += w
            reasons.append(f'RSI超卖({rsi:.0f},{w:.0f})')
        elif rsi > 70:
            score -= w
            reasons.append(f'RSI超买({rsi:.0f},{w:.0f})')

    # DMI
    if pdi and mdi:
        w = weights.get('DMI', 20)
        if pdi > mdi:
            score += w
            reasons.append(f'PDI>MDI({w:.0f})')
        else:
            score -= w
            reasons.append(f'MDI>PDI({w:.0f})')

    # ATR波动率（仅记录状态，不参与评分）
    if atr and last_price:
        atr_pct = atr / last_price * 100
        tech['volatility_pct'] = atr_pct
        tech['volatility_state'] = 'high' if atr_pct > 3 else ('low' if atr_pct < 1 else 'normal')

    # 成交量确认
    if obv is not None and obv_ma20 is not None:
        w = weights.get('VOLUME', 10)
        if obv > obv_ma20:
            score += w
            reasons.append(f'OBV>MA20({w:.0f})')
        elif obv < obv_ma20:
            score -= w
            reasons.append(f'OBV<MA20({w:.0f})')

    # ADX趋势强度过滤（震荡市场惩罚）
    # ADX < 18 → 无趋势（震荡），所有趋势信号打折
    # ADX 18-25 → 弱趋势，轻微打折
    # ADX > 25 → 有趋势，不打折
    adx = tech.get('ADX')
    if adx is not None:
        if adx < 18:
            # 无趋势（震荡市），所有趋势信号打3折
            score = int(score * 0.3)
            reasons.append(f'ADX={adx:.0f}<18震荡市(×0.3)')
        elif adx < 25:
            # 弱趋势，打6折
            score = int(score * 0.6)
            reasons.append(f'ADX={adx:.0f}<25弱趋势(×0.6)')

    # 趋势判断
    if score >= 30:
        trend = 'strong_bull'
    elif score >= 10:
        trend = 'weak_bull'
    elif score <= -30:
        trend = 'strong_bear'
    elif score <= -10:
        trend = 'weak_bear'
    else:
        trend = 'neutral'

    return {'score': score, 'trend': trend, 'reasons': reasons, 'market_state': market_state}


def compute_indicators(klines) -> dict:
    """从K线数据计算技术指标。返回tech字典。"""
    import tqsdk.ta as ta

    tech = {}

    # MA（含长周期MA40/MA60用于趋势结构确认）
    try:
        tech['MA5'] = safe_float(ta.MA(klines, 5).iloc[-1])
        tech['MA10'] = safe_float(ta.MA(klines, 10).iloc[-1])
        tech['MA20'] = safe_float(ta.MA(klines, 20).iloc[-1])
        tech['MA40'] = safe_float(ta.MA(klines, 40).iloc[-1])
        tech['MA60'] = safe_float(ta.MA(klines, 60).iloc[-1])
    except Exception:
        pass

    # MACD（只取DIF列，严禁取histogram/macd列）
    try:
        macd = ta.MACD(klines, 12, 26, 9)
        if hasattr(macd, 'columns'):
            # 严格只匹配DIF/DEA列，禁止匹配到MACD柱状图
            dif_col = None
            dea_col = None
            for col in macd.columns:
                col_lower = str(col).lower().strip()
                if col_lower in ('dif', 'diff') and dif_col is None:
                    dif_col = col
                elif col_lower in ('dea', 'signal') and dea_col is None:
                    dea_col = col
            if dif_col:
                tech['MACD_DIF'] = safe_float(macd[dif_col].iloc[-1])
            if dea_col:
                tech['MACD_DEA'] = safe_float(macd[dea_col].iloc[-1])
    except Exception:
        pass

    # RSI
    try:
        tech['RSI14'] = safe_float(ta.RSI(klines, 14).iloc[-1])
    except Exception:
        pass

    # DMI
    try:
        dmi = ta.DMI(klines, 14, 6)
        if hasattr(dmi, 'columns'):
            for col in ['pdi', 'PDI', '+DI']:
                if col in dmi.columns:
                    tech['DMI_PDI'] = safe_float(dmi[col].iloc[-1])
                    break
            for col in ['mdi', 'MDI', '-DI']:
                if col in dmi.columns:
                    tech['DMI_MDI'] = safe_float(dmi[col].iloc[-1])
                    break
    except Exception:
        pass

    # ATR
    try:
        tech['ATR14'] = safe_float(ta.ATR(klines, 14).iloc[-1])
    except Exception:
        pass

    # OBV
    try:
        import pandas as pd
        close_prices = klines['close']
        volumes = klines['volume']
        obv = [0]
        for i in range(1, len(close_prices)):
            if close_prices.iloc[i] > close_prices.iloc[i - 1]:
                obv.append(obv[-1] + volumes.iloc[i])
            elif close_prices.iloc[i] < close_prices.iloc[i - 1]:
                obv.append(obv[-1] - volumes.iloc[i])
            else:
                obv.append(obv[-1])
        tech['OBV'] = obv[-1]
        obv_series = pd.Series(obv)
        if len(obv_series) >= 20:
            tech['OBV_MA20'] = safe_float(obv_series.rolling(20).mean().iloc[-1])
    except Exception:
        pass

    return tech
