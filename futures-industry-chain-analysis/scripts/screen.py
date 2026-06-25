# -*- coding: utf-8 -*-
"""信号筛选模块：自下而上扫描所有品种，识别趋势初期信号。

核心逻辑：
1. 逐品种扫描技术指标
2. 识别趋势初期（MA刚排列、MACD刚金/死叉、RSI未过热）
3. 计算多指标共振度
4. 输出候选信号列表，按信号质量排序
"""

from typing import List, Dict, Optional


def detect_trend_stage(tech: dict, score: int) -> dict:
    """检测趋势阶段：early(初期) / mature(中期) / exhausted(末期)。

    判据：
    - early: MA刚排列或即将排列, MACD柱状线刚翻正/翻负, RSI 40-60区间
    - mature: MA已排列一段时间, MACD持续同向, RSI 50-70(多)或30-50(空)
    - exhausted: RSI >70(多)或 <30(空), 价格远离MA20
    """
    rsi = tech.get('RSI14')
    macd_dif = tech.get('MACD_DIF')
    ma5 = tech.get('MA5')
    ma10 = tech.get('MA10')
    ma20 = tech.get('MA20')
    last_price = tech.get('last_price')  # 需要从外部传入
    adx = tech.get('ADX')

    is_bull = score > 0
    stage_scores = {'early': 0, 'mature': 0, 'exhausted': 0}

    # RSI 判断
    if rsi is not None:
        if is_bull:
            if 40 <= rsi <= 60:
                stage_scores['early'] += 2  # RSI中性偏多=初期
            elif 60 < rsi <= 70:
                stage_scores['mature'] += 2
            elif rsi > 70:
                stage_scores['exhausted'] += 3  # 超买=末期
            elif rsi < 30:
                stage_scores['early'] += 1  # 超卖反弹=可能初期
        else:
            if 40 <= rsi <= 60:
                stage_scores['early'] += 2
            elif 30 <= rsi < 40:
                stage_scores['mature'] += 2
            elif rsi < 30:
                stage_scores['exhausted'] += 3  # 超卖=末期
            elif rsi > 70:
                stage_scores['early'] += 1  # 超买回落=可能初期

    # MA 排列判断（短周期+长周期综合）
    if ma5 is not None and ma10 is not None and ma20 is not None:
        ma40 = tech.get('MA40')
        ma60 = tech.get('MA60')
        if is_bull:
            if ma5 > ma10 and abs(ma5 - ma10) / ma10 < 0.005:
                stage_scores['early'] += 2  # MA5刚上穿MA10
            elif ma5 > ma10 > ma20:
                # 检查长周期是否共振
                if ma40 and ma60 and ma20 > ma40 > ma60:
                    stage_scores['mature'] += 2  # 全层级共振=成熟趋势
                else:
                    stage_scores['mature'] += 1
                # 检查是否排列过久（价格远离MA20）
                if last_price and last_price > ma20 * 1.05:
                    stage_scores['exhausted'] += 1
        else:
            if ma5 < ma10 and abs(ma5 - ma10) / ma10 < 0.005:
                stage_scores['early'] += 2
            elif ma5 < ma10 < ma20:
                if ma40 and ma60 and ma20 < ma40 < ma60:
                    stage_scores['mature'] += 2  # 全层级共振
                else:
                    stage_scores['mature'] += 1
                if last_price and last_price < ma20 * 0.95:
                    stage_scores['exhausted'] += 1

    # ADX 判断趋势强度
    if adx is not None:
        if 20 <= adx <= 35:
            stage_scores['early'] += 1  # 趋势刚形成
        elif adx > 40:
            stage_scores['mature'] += 1
        elif adx > 50:
            stage_scores['exhausted'] += 1  # 趋势过强

    # 判定阶段
    max_stage = max(stage_scores, key=stage_scores.get)
    total = sum(stage_scores.values()) or 1
    confidence = stage_scores[max_stage] / total

    return {
        'stage': max_stage,
        'confidence': round(confidence, 2),
        'detail': stage_scores,
    }


def count_resonance(tech: dict, score: int) -> dict:
    """计算多指标共振度。返回共振数和共振方向。

    共振指标：
    1. MA排列方向
    2. MACD DIF方向
    3. RSI方向（>50多, <50空）
    4. DMI方向（PDI>MDI多, 反之空）
    5. OBV方向（>MA20多, <MA20空）
    6. 价格位置（>MA20多, <MA20空）
    """
    is_bull = score > 0
    confirmations = 0
    total_checks = 0
    details = []

    # MA（短周期MA5/MA10/MA20 + 长周期MA40/MA60逐级验证）
    ma5, ma10, ma20 = tech.get('MA5'), tech.get('MA10'), tech.get('MA20')
    ma40, ma60 = tech.get('MA40'), tech.get('MA60')
    if ma5 and ma10 and ma20:
        total_checks += 1
        # 短周期排列
        short_bull = ma5 > ma10 > ma20
        short_bear = ma5 < ma10 < ma20
        # 长周期排列（如有MA40/MA60则参与验证）
        long_bull = (ma20 > ma40 > ma60) if (ma40 and ma60) else True
        long_bear = (ma20 < ma40 < ma60) if (ma40 and ma60) else True
        # 完全共振需要短+长周期同时满足
        full_bull = short_bull and long_bull
        full_bear = short_bear and long_bear
        if (is_bull and full_bull) or (not is_bull and full_bear):
            confirmations += 1
            details.append('MA排列✓' if (ma40 and ma60) else 'MA短周期✓')
        elif (is_bull and short_bull) or (not is_bull and short_bear):
            # 短周期满足但长周期未共振 → 半确认
            confirmations += 0.5
            details.append('MA短周期✓(长周期未共振)')
        elif short_bull or short_bear:
            details.append('MA排列✗')

    # MACD
    macd_dif = tech.get('MACD_DIF')
    if macd_dif is not None:
        total_checks += 1
        if (is_bull and macd_dif > 0) or (not is_bull and macd_dif < 0):
            confirmations += 1
            details.append('MACD✓')
        else:
            details.append('MACD✗')

    # RSI
    rsi = tech.get('RSI14')
    if rsi is not None:
        total_checks += 1
        if (is_bull and rsi > 50) or (not is_bull and rsi < 50):
            confirmations += 1
            details.append('RSI✓')
        else:
            details.append('RSI✗')

    # DMI
    pdi, mdi = tech.get('DMI_PDI'), tech.get('DMI_MDI')
    if pdi is not None and mdi is not None:
        total_checks += 1
        if (is_bull and pdi > mdi) or (not is_bull and mdi > pdi):
            confirmations += 1
            details.append('DMI✓')
        else:
            details.append('DMI✗')

    # OBV
    obv, obv_ma = tech.get('OBV'), tech.get('OBV_MA20')
    if obv is not None and obv_ma is not None:
        total_checks += 1
        if (is_bull and obv > obv_ma) or (not is_bull and obv < obv_ma):
            confirmations += 1
            details.append('OBV✓')
        else:
            details.append('OBV✗')

    # 价格位置
    last_price = tech.get('last_price')
    if last_price and ma20:
        total_checks += 1
        if (is_bull and last_price > ma20) or (not is_bull and last_price < ma20):
            confirmations += 1
            details.append('价格位✓')
        else:
            details.append('价格位✗')

    resonance_ratio = confirmations / total_checks if total_checks > 0 else 0

    return {
        'confirmations': confirmations,
        'total_checks': total_checks,
        'ratio': round(resonance_ratio, 2),
        'details': details,
    }


def screen_signals(symbols: List[dict], score_threshold: int = 20,
                   min_resonance: float = 0.5, exclude_exhausted: bool = True) -> List[dict]:
    """扫描所有品种，筛选出有交易价值的信号。

    筛选条件：
    1. |score| >= score_threshold（默认20）
    2. 共振度 >= min_resonance（默认50%指标同向）
    3. 趋势阶段不是 exhausted（可选）
    4. 市场整体偏空时，多头信号需要更高共振度（>=60%）

    返回：按信号质量排序的候选列表
    """
    # 判断市场整体环境
    buy_count = sum(1 for s in symbols if s.get('trend', {}).get('score', 0) > 20)
    sell_count = sum(1 for s in symbols if s.get('trend', {}).get('score', 0) < -20)
    market_bearish = sell_count > buy_count * 1.5  # 空头信号数量是多头的1.5倍以上
    market_bullish = buy_count > sell_count * 1.5

    candidates = []

    for sym in symbols:
        score = sym.get('trend', {}).get('score', 0)
        tech = sym.get('tech', {})
        trend_info = sym.get('trend', {})

        # 条件1: 信号强度
        if abs(score) < score_threshold:
            continue

        # 把 last_price 注入 tech 供内部使用
        tech_with_price = dict(tech)
        tech_with_price['last_price'] = sym.get('last_price')

        # 条件2: 趋势阶段
        stage = detect_trend_stage(tech_with_price, score)
        if exclude_exhausted and stage['stage'] == 'exhausted':
            continue

        # 条件3: 多指标共振
        resonance = count_resonance(tech_with_price, score)

        # 市场环境过滤：偏空市场对多头信号要求更高共振度
        direction = 'BUY' if score > 0 else 'SELL'
        required_resonance = min_resonance
        if market_bearish and direction == 'BUY':
            required_resonance = 0.6  # 偏空市场做多需要60%共振度
        elif market_bullish and direction == 'SELL':
            required_resonance = 0.6  # 偏多市场做空需要60%共振度

        if resonance['ratio'] < required_resonance:
            continue

        # 信号质量评分 = 信号强度 × 共振度 × 阶段系数
        stage_factor = {'early': 1.2, 'mature': 1.0, 'exhausted': 0.5}.get(stage['stage'], 0.8)
        signal_quality = round(abs(score) / 100.0 * resonance['ratio'] * stage_factor, 3)

        candidates.append({
            'product_id': sym['product_id'],
            'product_name': sym.get('product_name', sym['product_id']),
            'last_price': sym['last_price'],
            'open_interest': sym.get('open_interest', 0),
            'score': score,
            'direction': direction,
            'trend_stage': stage,
            'resonance': resonance,
            'signal_quality': signal_quality,
            'tech': tech,
            'trend': trend_info,
        })

    # 按信号质量排序（高置信度优先）
    candidates.sort(key=lambda x: x['signal_quality'], reverse=True)
    return candidates


def get_chain_for_symbol(product_id: str) -> Optional[str]:
    """O(1)查找品种所属产业链（从chains.py缓存读取）"""
    from .chains import get_chain_for_symbol as _cached_lookup
    return _cached_lookup(product_id)


def chain_verification(candidate: dict, chain_results: dict) -> dict:
    """产业链验证：检查品种信号是否与产业链方向一致。

    一致 → 加分（+0.15 置信度）
    背离 → 减分（-0.10 置信度）
    产业链震荡 → 不加不减
    """
    chain_name = get_chain_for_symbol(candidate['product_id'])
    if not chain_name or chain_name not in chain_results:
        return {
            'chain_name': chain_name or '未知',
            'chain_trend': '未知',
            'aligned': False,
            'confidence_adjustment': 0,
            'detail': '未找到产业链数据',
        }

    chain = chain_results[chain_name]
    chain_trend = chain['overall_trend']
    is_bull_signal = candidate['direction'] == 'BUY'

    # 判断是否对齐
    if chain_trend in ['多头趋势', '偏多震荡']:
        aligned = is_bull_signal
        if aligned:
            adj = 0.15
            detail = f'多头信号与{chain_name}多头趋势一致，置信度+15%'
        else:
            adj = -0.10
            detail = f'空头信号与{chain_name}多头趋势背离，置信度-10%'
    elif chain_trend in ['空头趋势', '偏空震荡']:
        aligned = not is_bull_signal
        if aligned:
            adj = 0.15
            detail = f'空头信号与{chain_name}空头趋势一致，置信度+15%'
        else:
            adj = -0.10
            detail = f'多头信号与{chain_name}空头趋势背离，置信度-10%'
    else:
        aligned = True  # 震荡市不惩罚
        adj = 0.0
        detail = f'{chain_name}处于震荡状态，不做方向性调整'

    # 产业链共振加分：同链多个品种同向
    same_direction_count = sum(
        1 for m in chain['members']
        if (candidate['direction'] == 'BUY' and m['score'] > 0) or
           (candidate['direction'] == 'SELL' and m['score'] < 0)
    )
    chain_ratio = same_direction_count / chain['count'] if chain['count'] > 0 else 0
    if chain_ratio >= 0.6:
        adj += 0.05
        detail += f'，同链{same_direction_count}/{chain["count"]}品种同向，共振+5%'

    return {
        'chain_name': chain_name,
        'chain_trend': chain_trend,
        'aligned': aligned,
        'confidence_adjustment': round(adj, 2),
        'detail': detail,
        'chain_avg_score': chain['avg_score'],
        'same_direction_ratio': round(chain_ratio, 2),
    }
