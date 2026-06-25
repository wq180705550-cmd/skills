# -*- coding: utf-8 -*-
"""多空辩论与研究主管裁决（信号级版本）。

自下而上逻辑：辩论对象是具体的品种信号，不是产业链整体。
- 多头：论证为什么这个做多信号值得跟随
- 空头：论证为什么这个信号可能失败
- 研究主管：基于信号强度+共振度+辩论结果，给出明确裁决
"""

from .config import get_chain_debate_weight


def bull_argument(chain_name: str, chain_data: dict, fundamental_data: dict = None) -> dict:
    """多头研究员：论证做多信号的有效性。

    chain_data 在自下而上模式中是单品种数据：
    - overall_trend: 品种自身趋势（如 'strong_bull', 'weak_bear'）
    - avg_score: 品种得分
    - leader: 品种代码
    - members[0]: 品种详情
    """
    weights = get_chain_debate_weight(chain_name)
    bull_case = {'chain': chain_name, 'arguments': [], 'strength': 0}

    score = chain_data.get('avg_score', 0)
    trend = chain_data.get('overall_trend', 'neutral')
    member = chain_data['members'][0] if chain_data.get('members') else {}
    price = member.get('price', 0)

    # 信号方向
    is_signal_bullish = score > 0

    # 技术面论证
    if is_signal_bullish:
        if trend in ('strong_bull', '多头趋势'):
            w = int(8 * weights['technical_weight'])
            bull_case['arguments'].append({
                'type': 'technical',
                'point': f'强势多头信号，得分{score:.0f}，趋势明确',
                'weight': w,
            })
            bull_case['strength'] += w
        elif trend in ('weak_bull', '偏多震荡'):
            w = int(6 * weights['technical_weight'])
            bull_case['arguments'].append({
                'type': 'technical',
                'point': f'偏多信号，得分{score:.0f}，趋势初步形成',
                'weight': w,
            })
            bull_case['strength'] += w
        else:
            # 信号与趋势矛盾（可能是反转信号）
            w = int(3 * weights['technical_weight'])
            bull_case['arguments'].append({
                'type': 'technical',
                'point': f'多头信号与当前趋势矛盾(得分{score:.0f})，可能是反转初期',
                'weight': w,
            })
            bull_case['strength'] += w

    # 持仓量论证（高持仓=信号更可靠）
    oi = member.get('oi', 0)
    if oi > 100000:
        w = int(4 * weights.get('fundamental_weight', 1.0))
        bull_case['arguments'].append({
            'type': 'position',
            'point': f'高持仓量({oi:,})，市场关注度高，信号可靠性强',
            'weight': w,
        })
        bull_case['strength'] += w
    elif oi > 50000:
        w = int(2 * weights.get('fundamental_weight', 1.0))
        bull_case['arguments'].append({
            'type': 'position',
            'point': f'持仓量({oi:,})适中',
            'weight': w,
        })
        bull_case['strength'] += w

    # 产业链逻辑
    debate_unit = chain_data.get('debate_unit', {})
    if debate_unit.get('focus'):
        w = int(3 * weights['chain_logic_weight'])
        bull_case['arguments'].append({
            'type': 'chain_logic',
            'point': f'产业链逻辑：{debate_unit["focus"]}',
            'weight': w,
        })
        bull_case['strength'] += w

    return bull_case


def bear_argument(chain_name: str, chain_data: dict, fundamental_data: dict = None) -> dict:
    """空头研究员：论证信号可能失败的风险。"""
    weights = get_chain_debate_weight(chain_name)
    bear_case = {'chain': chain_name, 'arguments': [], 'strength': 0}

    score = chain_data.get('avg_score', 0)
    trend = chain_data.get('overall_trend', 'neutral')
    member = chain_data['members'][0] if chain_data.get('members') else {}

    is_signal_bullish = score > 0

    # 技术面风险
    if is_signal_bullish:
        # 做多信号的风险论证
        if trend in ('strong_bull',):
            w = int(2 * weights['technical_weight'])
            bear_case['arguments'].append({
                'type': 'technical',
                'point': f'趋势已强(得分{score:.0f})，可能接近阶段性顶部',
                'weight': w,
            })
            bear_case['strength'] += w
        elif trend in ('weak_bear', '空头趋势'):
            w = int(6 * weights['technical_weight'])
            bear_case['arguments'].append({
                'type': 'technical',
                'point': f'多头信号在空头趋势中(得分{score:.0f})，可能只是反弹',
                'weight': w,
            })
            bear_case['strength'] += w
        else:
            w = int(3 * weights['technical_weight'])
            bear_case['arguments'].append({
                'type': 'technical',
                'point': f'信号强度一般(得分{score:.0f})，持续性存疑',
                'weight': w,
            })
            bear_case['strength'] += w
    else:
        # 做空信号的风险论证
        if trend in ('strong_bear',):
            w = int(2 * weights['technical_weight'])
            bear_case['arguments'].append({
                'type': 'technical',
                'point': f'空头趋势已强(得分{score:.0f})，可能接近阶段性底部',
                'weight': w,
            })
            bear_case['strength'] += w
        elif trend in ('weak_bull', '多头趋势'):
            w = int(6 * weights['technical_weight'])
            bear_case['arguments'].append({
                'type': 'technical',
                'point': f'空头信号在多头趋势中(得分{score:.0f})，可能只是回调',
                'weight': w,
            })
            bear_case['strength'] += w
        else:
            w = int(3 * weights['technical_weight'])
            bear_case['arguments'].append({
                'type': 'technical',
                'point': f'空头信号强度一般(得分{score:.0f})',
                'weight': w,
            })
            bear_case['strength'] += w

    # 通用风险因素
    w = int(3 * weights.get('macro_weight', 1.0))
    bear_case['arguments'].append({
        'type': 'risk',
        'point': '技术指标滞后性、突发消息风险',
        'weight': w,
    })
    bear_case['strength'] += w

    # 持仓量风险
    oi = member.get('oi', 0)
    if oi < 30000:
        w = int(3 * weights.get('fundamental_weight', 1.0))
        bear_case['arguments'].append({
            'type': 'position',
            'point': f'持仓量偏低({oi:,})，流动性风险',
            'weight': w,
        })
        bear_case['strength'] += w

    return bear_case


def research_manager_decision(bull_case: dict, bear_case: dict, chain_trend: str = '') -> dict:
    """研究主管：裁决信号辩论。

    自下而上逻辑：
    - 辩论是针对具体信号的，不是产业链整体
    - 信号方向由 score 决定，辩论决定信号是否值得跟随
    - strength_diff > 0 表示信号论据更充分
    """
    diff = bull_case['strength'] - bear_case['strength']

    if diff > 3:
        verdict = 'BUY'
        plan = f'做多论证较强(+{diff})，信号有效'
    elif diff < -3:
        verdict = 'SELL'
        plan = f'做空论证较强(+{-diff})，信号有效'
    else:
        verdict = 'HOLD'
        plan = '多空势均力敌，信号可靠性不足'

    return {
        'chain': bull_case['chain'],
        'bull_strength': bull_case['strength'],
        'bear_strength': bear_case['strength'],
        'verdict': verdict,
        'plan': plan,
    }
