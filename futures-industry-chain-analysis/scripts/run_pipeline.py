# -*- coding: utf-8 -*-
"""主入口：自下而上分析管道（信号筛选→信号辩论→产业链验证→置信度排序→风险评估→报告）。

核心原则：
1. 自下而上：先扫描每个品种的信号，再做产业链验证
2. 置信度优先：保证胜率，然后保证高盈亏比
3. 趋势初期优先：优先发现刚启动的趋势，避免追高/追空
"""

import json
import os
import time


def run_pipeline(
    output_dir: str = None,
    data_dir: str = None,
    skip_debate: bool = False
) -> dict:
    """执行自下而上的产业链分析流程。"""
    if skip_debate:
        print("\n⚡ 辩论已跳过：直接使用信号方向计算置信度\n")

    # 默认路径解析（基于用户Documents目录，非硬编码）
    import platform
    _home = os.path.expanduser('~')
    _base = os.path.join(_home, 'Documents', 'WorkBuddy')
    if output_dir is None:
        output_dir = os.path.join(_base, 'Commodities', 'Reports', 'industry-chain')
    if data_dir is None:
        data_dir = os.path.join(_base, 'Commodities', 'Temp')

    # 懒加载：仅在运行时导入
    from .screen import screen_signals, chain_verification, get_chain_for_symbol
    from .chains import cluster_chains, CHAIN_PRODUCTS, DEBATE_UNITS
    from .debate import bull_argument, bear_argument, research_manager_decision
    from .trade_plan import generate_trade_plan, calc_confidence, calc_adaptive_target
    from .risk import (aggressive_risk_assessment, conservative_risk_assessment,
                       neutral_risk_assessment, risk_manager_decision)
    from .report import generate_markdown_report, generate_html_report

    # ================================================================
    # Phase 1: 加载数据
    # ================================================================
    market_data_path = os.path.join(data_dir, 'market_data.json')
    with open(market_data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    symbols = data['symbols']
    sym_map = {s['product_id']: s for s in symbols}

    # ================================================================
    # Phase 2: 产业链聚类（用于后续验证，不用于决策）
    # ================================================================
    chain_results = cluster_chains(symbols)

    # ================================================================
    # Phase 3: 信号筛选（自下而上的核心）
    # 扫描所有品种，找出趋势初期+多指标共振的信号
    # ================================================================
    candidates = screen_signals(
        symbols,
        score_threshold=20,     # |得分| >= 20
        min_resonance=0.5,      # 至少50%指标同向
        exclude_exhausted=True, # 排除趋势末期
    )

    # ================================================================
    # Phase 4: 逐品种信号辩论（可跳过） + 产业链验证 + 置信度计算
    # ================================================================
    all_opportunities = []

    for cand in candidates:
        signal_direction = cand['direction']
        chain_name = get_chain_for_symbol(cand['product_id'])

        # 4a. 信号级辩论（skip_debate=True 时跳过）
        if not skip_debate:
            # 构建单品种辩论上下文
            debate_context = {
                'overall_trend': cand['trend'].get('trend', 'neutral'),
                'avg_score': cand['score'],
                'leader': cand['product_id'],
                'leader_price': cand['last_price'],
                'count': 1,
                'members': [{
                    'pid': cand['product_id'],
                    'name': cand['product_name'],
                    'price': cand['last_price'],
                    'score': cand['score'],
                    'trend': cand['trend'].get('trend', 'N/A'),
                    'oi': cand['open_interest'],
                }],
                'debate_unit': DEBATE_UNITS.get(chain_name, {}),
            }

            bull = bull_argument(chain_name or '未知', debate_context)
            bear = bear_argument(chain_name or '未知', debate_context)

            debate_decision = research_manager_decision(
                bull, bear, debate_context['overall_trend']
            )

            debate_aligned = (
                (signal_direction == 'BUY' and debate_decision['verdict'] == 'BUY') or
                (signal_direction == 'SELL' and debate_decision['verdict'] == 'SELL')
            )
            debate_neutral = debate_decision['verdict'] == 'HOLD'
        else:
            # 跳过辩论：直接使用信号方向，无辩论调整
            debate_aligned = True
            debate_neutral = False
            bull = {'strength': 0, 'arguments': ['辩论已跳过']}
            bear = {'strength': 0, 'arguments': ['辩论已跳过']}
            debate_decision = {'verdict': signal_direction, 'reasoning': '跳过辩论'}

        # 4b. 产业链验证
        chain_verify = chain_verification(cand, chain_results)
        chain_direction = chain_verify.get('chain_trend', '震荡')

        # 4c. 计算置信度（使用 trade_plan.py 的 calc_confidence，确保一致性）
        confidence = calc_confidence(cand['score'], cand['tech'], chain_direction)
        # 叠加产业链验证调整
        confidence = min(max(confidence + chain_verify['confidence_adjustment'], 0.0), 1.0)

        # 辩论不一致时大幅降权（skip_debate时不调整）
        if not skip_debate:
            if debate_aligned:
                pass  # 一致，不调整
            elif debate_neutral:
                confidence *= 0.85  # HOLD中性结果，轻微降权
            else:
                confidence *= 0.6  # 辩论结果与信号方向矛盾，大幅降权

        # 市场环境判断（双向检查，防止偏空/偏多市场误判）
        # 阈值通过CONFIG_MANAGER配置，默认为60%同向判定为趋势市场
        from .config import CONFIG_MANAGER
        _market_threshold = CONFIG_MANAGER.get('market_state', {}).get('trend_threshold', 60) / 100.0
        _chain_count = len(chain_results)
        _bear_chains = sum(1 for cr in chain_results.values() if '空' in cr.get('overall_trend', ''))
        _bull_chains = sum(1 for cr in chain_results.values() if '多' in cr.get('overall_trend', ''))
        market_bearish = _bear_chains > _chain_count * _market_threshold
        market_bullish = _bull_chains > _chain_count * _market_threshold

        if market_bearish and signal_direction == 'BUY':
            confidence *= 0.8  # 偏空市场做多，额外惩罚20%
        elif market_bullish and signal_direction == 'SELL':
            confidence *= 0.8  # 偏空市场做多，额外惩罚20%

        # 4d. 生成交易方案
        atr = cand['tech'].get('ATR14', 0)
        volatility = cand['tech'].get('volatility_pct', 0.02) / 100.0 if cand['tech'].get('volatility_pct') else 0.02

        sym_data = {
            'pid': cand['product_id'],
            'price': cand['last_price'],
            'score': cand['score'],
            'atr': atr,
            'volatility': volatility,
        }

        trade_plan = generate_trade_plan(sym_data, chain_direction, cand['tech'])

        # 严格检查：只有当 trade_plan 不是 HOLD 时才继续
        # 不再绕过置信度阈值
        if trade_plan['decision'] == 'HOLD':
            # 记录被过滤的原因，但不纳入推荐
            continue

        # 更新置信度到交易方案（使用调整后的置信度）
        trade_plan['confidence'] = round(confidence, 3)
        trade_plan['recommend_score'] = round(
            confidence * 0.7 + min(trade_plan.get('risk_reward_ratio', 0) / 3.0, 1.0) * 0.3, 3
        )

        # 二次过滤：调整后置信度仍需 >= 0.4
        if confidence < 0.4:
            continue

        # 只保留有效的交易机会
        if trade_plan['decision'] != 'HOLD':
            all_opportunities.append({
                'product_id': cand['product_id'],
                'product_name': cand['product_name'],
                'direction': trade_plan['decision'],
                'signal_quality': cand['signal_quality'],
                'trend_stage': cand['trend_stage'],
                'resonance': cand['resonance'],
                'chain_verify': chain_verify,
                'debate': {
                    'bull_strength': bull['strength'],
                    'bear_strength': bear['strength'],
                    'verdict': debate_decision['verdict'],
                    'aligned': debate_aligned,
                },
                'trade_plan': trade_plan,
            })

    # ================================================================
    # Phase 5: 置信度排序（核心输出）
    # 主排序：置信度（胜率优先）
    # 次排序：盈亏比（高赔率优先）
    # ================================================================
    all_opportunities.sort(
        key=lambda x: (x['trade_plan']['confidence'], x['trade_plan'].get('risk_reward_ratio', 0)),
        reverse=True,
    )

    # 分组：多头机会 / 空头机会
    buy_opps = [o for o in all_opportunities if o['direction'] == 'BUY']
    sell_opps = [o for o in all_opportunities if o['direction'] == 'SELL']

    # ================================================================
    # Phase 6: 风险评估（仅对 Top 机会）
    # ================================================================
    risk_assessments = {}
    for opp in all_opportunities[:10]:  # Top 10 做风险评估
        tp = opp['trade_plan']
        agg = aggressive_risk_assessment(tp)
        con = conservative_risk_assessment(tp)
        neu = neutral_risk_assessment(tp)
        rd = risk_manager_decision(agg, con, neu, tp)
        risk_assessments[opp['product_id']] = {
            'aggressive': agg, 'conservative': con, 'neutral': neu, 'risk_decision': rd,
        }

    # ================================================================
    # Phase 7: 生成报告
    # ================================================================
    data_source = data.get('meta', {}).get('source', 'auto')
    md_report = generate_markdown_report(
        chain_results, all_opportunities, buy_opps, sell_opps,
        risk_assessments, data_source
    )
    html_report = generate_html_report(
        chain_results, all_opportunities, buy_opps, sell_opps,
        risk_assessments, data_source
    )

    os.makedirs(output_dir, exist_ok=True)
    date_compact = time.strftime('%Y%m%d')

    md_path = os.path.join(output_dir, f'chain_report_{date_compact}.md')
    html_path = os.path.join(output_dir, f'chain_report_{date_compact}.html')

    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md_report)
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_report)

    return {
        'chain_results': chain_results,
        'all_opportunities': all_opportunities,
        'buy_opportunities': buy_opps,
        'sell_opportunities': sell_opps,
        'risk_assessments': risk_assessments,
        'report_paths': {'md': md_path, 'html': html_path},
        'skip_debate': skip_debate,
        'stats': {
            'total_symbols': len(symbols),
            'candidates_screened': len(candidates),
            'opportunities_found': len(all_opportunities),
            'buy_count': len(buy_opps),
            'sell_count': len(sell_opps),
        },
    }
