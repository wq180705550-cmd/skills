# -*- coding: utf-8 -*-
"""交易方案生成：置信度、盈亏比、综合排序。"""


def calc_confidence(symbol_score: int, tech_indicators: dict, chain_direction: str) -> float:
    """计算品种置信度 (0.0 ~ 1.0)。

    公式：信号强度50% + 多指标共振25% + 产业链验证25%
    """
    signal_strength = abs(symbol_score) / 100.0

    confirmations = 0
    is_bullish = symbol_score > 0
    if is_bullish:
        if tech_indicators.get('RSI14', 50) > 50: confirmations += 1
        if tech_indicators.get('MACD_DIF', 0) > 0: confirmations += 1
        if tech_indicators.get('DMI_PDI', 0) > tech_indicators.get('DMI_MDI', 0): confirmations += 1
    else:
        if tech_indicators.get('RSI14', 50) < 50: confirmations += 1
        if tech_indicators.get('MACD_DIF', 0) < 0: confirmations += 1
        if tech_indicators.get('DMI_MDI', 0) > tech_indicators.get('DMI_PDI', 0): confirmations += 1

    indicator_resonance = confirmations / 3.0

    chain_base = 0.5
    if chain_direction in ['多头趋势', '空头趋势']:
        aligned = (is_bullish and chain_direction == '多头趋势') or (not is_bullish and chain_direction == '空头趋势')
        chain_adjustment = 0.20 if aligned else -0.10
    else:
        chain_adjustment = 0.0

    confidence = 0.50 * signal_strength + 0.25 * indicator_resonance + 0.25 * (chain_base + chain_adjustment)
    return round(min(max(confidence, 0.0), 1.0), 3)


def calc_adaptive_target(current_price: float, atr_value: float, daily_volatility: float,
                         direction: str, tech_data: dict = None) -> float:
    """按品种波动率分档计算目标价。目标至少为ATR×1.5，确保盈亏比≥1。"""
    if daily_volatility > 0.03:
        base_pct = 0.06
    elif daily_volatility > 0.015:
        base_pct = 0.04
    else:
        base_pct = 0.03

    adx = (tech_data or {}).get('ADX', 25)
    adx_mult = 1.3 if adx > 30 else (0.7 if adx < 20 else 1.0)
    base_target = current_price * base_pct * adx_mult

    # ATR基准目标：至少ATR×2.0，确保盈亏比≥1（止损=ATR×2）
    atr_target = atr_value * 2.0 if atr_value > 0 else 0
    base_target = max(base_target, atr_target)

    # 关键技术位
    tech_targets = []
    if tech_data:
        for key in ['recent_high', 'recent_low', 'MA20', 'MA60']:
            val = tech_data.get(key)
            if val is None:
                continue
            if direction == 'BUY' and val > current_price:
                tech_targets.append(val - current_price)
            elif direction == 'SELL' and val < current_price:
                tech_targets.append(current_price - val)

    target_dist = min(base_target, min(tech_targets)) if tech_targets else base_target
    return round(current_price + target_dist if direction == 'BUY' else current_price - target_dist, 2)


def normalize_risk_reward(rr: float) -> float:
    """盈亏比标准化到 0-1。"""
    return min(rr / 3.0, 1.0)


def calc_recommend_score(confidence: float, rr: float) -> float:
    """推荐分 = 置信度×0.7 + 盈亏比标准化×0.3。"""
    return round(confidence * 0.70 + normalize_risk_reward(rr) * 0.30, 3)


def generate_trade_plan(symbol_data: dict, chain_direction: str, tech_data: dict = None) -> dict:
    """生成交易方案（自下而上+置信度优先）。"""
    price = symbol_data['price']
    score = symbol_data['score']
    atr = symbol_data.get('atr', 0)
    daily_vol = symbol_data.get('volatility', 0.02)

    if score >= 20:
        direction = 'BUY'
    elif score <= -20:
        direction = 'SELL'
    else:
        return {'pid': symbol_data['pid'], 'decision': 'HOLD', 'confidence': 0, 'recommend_score': 0,
                'reason': f'信号强度不足(|得分|={abs(score)}<20)'}

    confidence = calc_confidence(score, tech_data or {}, chain_direction)
    if confidence < 0.4:
        return {'pid': symbol_data['pid'], 'decision': 'HOLD', 'confidence': confidence, 'recommend_score': 0,
                'reason': f'置信度过低({confidence:.1%}<40%)'}

    # 止损
    if direction == 'BUY':
        entry = price
        stop_loss = price - atr * 2.0 if atr > 0 else price * 0.95
    else:
        entry = price
        stop_loss = price + atr * 2.0 if atr > 0 else price * 1.05

    # 目标价
    target = calc_adaptive_target(price, atr, daily_vol, direction, tech_data)

    # 盈亏比（确保目标价至少等于止损距离，保证盈亏比≥1）
    reward = abs(target - entry)
    risk = abs(entry - stop_loss)
    if risk > 0 and reward < risk:
        # 目标价太近，强制调整为至少等于止损距离
        if direction == 'BUY':
            target = round(entry + risk, 2)
        else:
            target = round(entry - risk, 2)
        reward = abs(target - entry)

    rr = round(reward / risk, 2) if risk > 0 else 0
    if rr < 0.8:
        return {'pid': symbol_data['pid'], 'decision': 'HOLD', 'confidence': confidence, 'recommend_score': 0,
                'reason': f'盈亏比不足({rr}:1<0.8:1)'}

    recommend_score = calc_recommend_score(confidence, rr)

    # 仓位
    base = 5.0
    pos_mult = 1.2 if confidence > 0.7 else (0.7 if confidence < 0.5 else 1.0)
    vol_mult = 0.7 if daily_vol > 0.03 else (1.2 if daily_vol < 0.015 else 1.0)
    pos = round(min(max(base * pos_mult * vol_mult, 2.0), 8.0), 1)

    return {
        'pid': symbol_data['pid'],
        'decision': direction,
        'entry_price': round(entry, 2),
        'target_price': target,
        'stop_loss': round(stop_loss, 2),
        'risk_reward_ratio': rr,
        'confidence': confidence,
        'recommend_score': recommend_score,
        'position_size': f'{pos}%',
        'validity': '1-3日',
    }


def rank_all_candidates(all_plans: list) -> dict:
    """按推荐分排序，输出 Top 5 多头/空头。"""
    actionable = [p for p in all_plans if p['decision'] != 'HOLD']
    bullish = sorted([p for p in actionable if p['decision'] == 'BUY'], key=lambda x: x['recommend_score'], reverse=True)[:5]
    bearish = sorted([p for p in actionable if p['decision'] == 'SELL'], key=lambda x: x['recommend_score'], reverse=True)[:5]
    return {'bullish_top5': bullish, 'bearish_top5': bearish}
