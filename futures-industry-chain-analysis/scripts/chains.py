# -*- coding: utf-8 -*-
"""产业链定义、聚类分析、龙头选择、反转映射缓存。"""

from typing import Dict, List, Optional

# 产业链品种映射
CHAIN_PRODUCTS: Dict[str, List[str]] = {
    '黑色系':   ['i', 'j', 'jm', 'rb', 'hc', 'SF', 'SM'],
    '能源链':   ['sc', 'lu', 'fu', 'bu', 'pg', 'ec'],
    '聚酯链':   ['PX', 'TA', 'PF', 'PR'],
    '油化工':   ['eg', 'eb', 'v', 'pp', 'l', 'PL', 'ps', 'bz'],
    '煤化工':   ['MA', 'SH'],
    '有色':     ['cu', 'al', 'zn', 'pb', 'ni', 'sn', 'ao', 'bc', 'si', 'SS', 'ad', 'lc'],
    '贵金属':   ['au', 'ag', 'pt'],
    '油脂油料': ['a', 'b', 'm', 'y', 'p', 'OI', 'RM', 'PK'],
    '谷物软商品': ['c', 'cs', 'SR', 'CF', 'CY', 'jd', 'lh', 'AP', 'CJ', 'rr'],
    '建材':     ['FG', 'SA', 'UR'],
    '橡胶':     ['ru', 'nr', 'br'],
    '纸浆造纸': ['sp', 'op'],
}

# ==================== 缓存加速 ====================

# 反向映射：品种代码 → 产业链名称（运行一次后缓存）
_PRODUCT_TO_CHAIN: Dict[str, str] = {}

def _build_reverse_map():
    """构建品种→产业链的反向映射表（仅构建一次）"""
    global _PRODUCT_TO_CHAIN
    if not _PRODUCT_TO_CHAIN:
        for chain_name, products in CHAIN_PRODUCTS.items():
            for pid in products:
                _PRODUCT_TO_CHAIN[pid] = chain_name

def get_all_products() -> List[str]:
    """获取所有品种代码列表"""
    _build_reverse_map()
    return list(_PRODUCT_TO_CHAIN.keys())

def get_chain_for_symbol(product_id: str) -> Optional[str]:
    """O(1)查找品种所属产业链"""
    _build_reverse_map()
    return _PRODUCT_TO_CHAIN.get(product_id)

# 辩论单元
DEBATE_UNITS: Dict[str, dict] = {
    '黑色系':   {'unit': ['i', 'j', 'rb'], 'focus': '成本推涨vs需求拉动？利润在上游还是下游？'},
    '能源链':   {'unit': ['sc', 'lu', 'bu'], 'focus': '裂解价差？原油-成品油传导效率？'},
    '聚酯链':   {'unit': ['PX', 'TA', 'PF'], 'focus': '聚酯利润？PX-PTA价差？'},
    '油化工':   {'unit': ['eg', 'pp', 'l'], 'focus': '烯烃利润？原油-化工品传导？'},
    '煤化工':   {'unit': ['MA', 'SH'], 'focus': 'MTO/MTP价差？煤-甲醇传导？'},
    '有色':     {'unit': ['ao', 'al', 'ni', 'lc'], 'focus': '氧化铝→铝的成本传导？镍→不锈钢？碳酸锂→新能源需求？'},
    '贵金属':   {'unit': ['au', 'ag'], 'focus': '黄金-白银比价，避险情绪传导'},
    '油脂油料': {'unit': ['m', 'y', 'p'], 'focus': '压榨利润？油脂间替代关系？'},
    '谷物软商品': {'unit': ['c', 'CF', 'lh'], 'focus': '农产品供需周期？养殖利润？'},
    '建材':     {'unit': ['FG', 'SA', 'UR'], 'focus': '纯碱→玻璃成本传导？'},
    '橡胶':     {'unit': ['ru', 'nr', 'br'], 'focus': '天然vs合成橡胶价差？'},
    '纸浆造纸': {'unit': ['sp', 'op'], 'focus': '纸浆-双胶纸价差？sp为上游（纸浆），op为下游（双胶纸）'},
}

# 产业链相关性矩阵
CHAIN_CORRELATION_MATRIX: Dict[str, Dict[str, float]] = {
    '黑色系':   {'能源链': 0.3, '有色': 0.4, '建材': 0.6},
    '能源链':   {'黑色系': 0.3, '聚酯链': 0.7, '油化工': 0.8},
    '聚酯链':   {'能源链': 0.7, '油化工': 0.6},
    '油化工':   {'能源链': 0.8, '聚酯链': 0.6, '煤化工': 0.5},
    '煤化工':   {'油化工': 0.5, '能源链': 0.4},
    '有色':     {'黑色系': 0.4, '贵金属': 0.3},
    '贵金属':   {'有色': 0.3},
    '油脂油料': {'谷物软商品': 0.5},
    '谷物软商品': {'油脂油料': 0.5},
    '建材':     {'黑色系': 0.6},
    '橡胶':     {'能源链': 0.4},
    '纸浆造纸': {},
}


def classify_chain(avg_score: float) -> str:
    """根据平均得分判断产业链整体趋势。"""
    if avg_score >= 20:
        return '多头趋势'
    elif avg_score >= 5:
        return '偏多震荡'
    elif avg_score <= -20:
        return '空头趋势'
    elif avg_score <= -5:
        return '偏空震荡'
    return '震荡'


def _get_score(s):
    """获取品种趋势评分（兼容trend.score和tech.score两种格式）。"""
    return s.get('trend', {}).get('score') or s.get('tech', {}).get('score', 0)


def select_leader(chain_symbols: list, overall_trend: str):
    """按趋势方向选择龙头品种。"""
    if overall_trend in ('多头趋势', '偏多震荡'):
        leader = max(chain_symbols, key=lambda x: _get_score(x))
        reason = '趋势得分最高（领涨）'
    elif overall_trend in ('空头趋势', '偏空震荡'):
        leader = min(chain_symbols, key=lambda x: _get_score(x))
        reason = '趋势得分最低（领跌）'
    else:
        leader = max(chain_symbols, key=lambda x: x.get('tech', {}).get('ATR14', 0) or 0)
        reason = '波动率最高（ATR最大，弹性最好）'
    return leader, reason


def cluster_chains(symbols: list) -> dict:
    """将品种数据按产业链聚类。"""
    chain_results = {}
    # 构建大小写不敏感的产品映射
    products_upper = {chain_name: [p.upper() for p in products] for chain_name, products in CHAIN_PRODUCTS.items()}
    for chain_name, products in CHAIN_PRODUCTS.items():
        chain_symbols = [s for s in symbols if s.get('product_id', '').upper() in products_upper[chain_name]]
        if not chain_symbols:
            continue

        total_score = sum(s.get('trend', {}).get('score', 0) or s.get('tech', {}).get('score', 0) for s in chain_symbols)
        avg_score = total_score / len(chain_symbols) if chain_symbols else 0
        overall_trend = classify_chain(avg_score)
        leader, leader_reason = select_leader(chain_symbols, overall_trend)

        chain_results[chain_name] = {
            'count': len(chain_symbols),
            'leader': leader.get('product_id'),
            'leader_price': leader.get('last_price'),
            'leader_reason': leader_reason,
            'overall_trend': overall_trend,
            'avg_score': round(avg_score, 1),
            'debate_unit': DEBATE_UNITS.get(chain_name, {}),
            'members': [
                {
                    'pid': s['product_id'],
                    'name': s.get('product_name', s['product_id']),
                    'price': s['last_price'],
                    'score': _get_score(s),
                    'trend': s.get('trend', {}).get('trend', s.get('tech', {}).get('trend', 'N/A')),
                    'oi': s['open_interest'],
                }
                for s in chain_symbols
            ],
        }
    return chain_results
