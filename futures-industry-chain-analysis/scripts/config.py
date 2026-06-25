# -*- coding: utf-8 -*-
"""配置管理模块：系统参数、自适应权重、品种阈值、产业链辩论权重。"""

# ============================================================
# 系统配置
# ============================================================
CONFIG_MANAGER = {
    'system': {
        'version': '2.8',
        'debug': False,
        'log_level': 'INFO',
        'max_symbols': 50,
        'min_open_interest': 10000,
        'enable_cache': True,
        'cache_ttl': 300,
        'parallel_processing': True,
        'max_workers': 4,
    },

    # 自适应权重系统
    'adaptive_weights': {
        'market_state_factors': {
            'trending':  {'MA': 1.2, 'MACD': 1.1, 'RSI': 0.8, 'DMI': 1.3, 'VOLUME': 0.9, 'PRICE_POSITION': 1.0},
            'ranging':   {'MA': 0.8, 'MACD': 0.9, 'RSI': 1.3, 'DMI': 0.7, 'VOLUME': 1.2, 'PRICE_POSITION': 1.1},
            'volatile':  {'MA': 0.9, 'MACD': 1.0, 'RSI': 1.1, 'DMI': 1.0, 'VOLUME': 1.3, 'PRICE_POSITION': 0.8},
        },
        'product_type_factors': {
            'industrial':    {'MA': 1.0, 'MACD': 1.1, 'RSI': 0.9, 'DMI': 1.2, 'VOLUME': 1.0, 'PRICE_POSITION': 1.0},
            'agricultural':  {'MA': 0.9, 'MACD': 0.8, 'RSI': 1.2, 'DMI': 0.9, 'VOLUME': 1.3, 'PRICE_POSITION': 1.1},
            'financial':     {'MA': 1.1, 'MACD': 1.0, 'RSI': 1.0, 'DMI': 1.1, 'VOLUME': 0.9, 'PRICE_POSITION': 1.0},
        },
        'default_weights': {
            'MA': 30, 'MACD': 20, 'RSI': 10, 'DMI': 20, 'VOLUME': 10, 'PRICE_POSITION': 15,
        },
    },

    # 品种特异性阈值
    'product_thresholds': {
        'black':       {'warrant_low': 800,  'warrant_high': 4000, 'volatility_threshold': 2.5},
        'energy':      {'warrant_low': 1000, 'warrant_high': 5000, 'volatility_threshold': 3.0},
        'nonferrous':  {'warrant_low': 1200, 'warrant_high': 6000, 'volatility_threshold': 2.8},
        'precious':    {'warrant_low': 500,  'warrant_high': 3000, 'volatility_threshold': 2.0},
        'agricultural':{'warrant_low': 1500, 'warrant_high': 7000, 'volatility_threshold': 3.5},
        'default':     {'warrant_low': 1000, 'warrant_high': 5000, 'volatility_threshold': 3.0},
    },

    # 市场状态识别
    'market_state': {
        'trend_threshold': 25,
        'range_threshold': 10,
        'volatile_threshold': 2.0,
        'adx_trend': 25,
        'adx_range': 20,
    },

    # 交易参数
    'trading': {
        'entry_atr_multiplier': 0.5,
        'entry_validity_hours': 4,
        'use_market_order': True,
        'target_return': 0.10,
        'atr_multiplier': 2.0,
        'max_position': 8,
        'min_position': 2,
        'base_position': 5,
    },

    # 风险参数
    'risk': {
        'max_drawdown': 20,
        'sharpe_ratio_min': 1.0,
        'win_rate_min': 50,
    },

    # 产业链特有指标
    'chain_specific_indicators': {
        '贵金属':   {'required': ['实际利率', '美元指数DXY', '央行购金', 'ETF持仓'], 'type': 'macro_driven'},
        '油脂油料': {'required': ['天气因子', 'USDA报告', '压榨利润', '库存'], 'type': 'supply_driven'},
        '谷物软商品': {'required': ['天气因子', '产量预估', '政策因子', '库存'], 'type': 'supply_driven'},
        '黑色系':   {'required': ['钢厂利润', '房地产数据', '基建投资', '仓单'], 'type': 'demand_driven'},
        '能源链':   {'required': ['裂解价差', '原油库存', 'OPEC+政策', '炼油厂开工率'], 'type': 'supply_demand'},
    },

    # 产业链辩论权重
    'chain_debate_weights': {
        '黑色系':   {'technical_weight': 1.2, 'fundamental_weight': 1.3, 'chain_logic_weight': 1.1, 'macro_weight': 0.8},
        '能源链':   {'technical_weight': 1.0, 'fundamental_weight': 1.4, 'chain_logic_weight': 1.3, 'macro_weight': 1.2},
        '聚酯链':   {'technical_weight': 1.0, 'fundamental_weight': 1.2, 'chain_logic_weight': 1.2, 'macro_weight': 0.9},
        '油化工':   {'technical_weight': 1.0, 'fundamental_weight': 1.1, 'chain_logic_weight': 1.2, 'macro_weight': 1.1},
        '煤化工':   {'technical_weight': 1.0, 'fundamental_weight': 1.0, 'chain_logic_weight': 1.3, 'macro_weight': 0.7},
        '有色':     {'technical_weight': 1.1, 'fundamental_weight': 1.2, 'chain_logic_weight': 1.0, 'macro_weight': 1.3},
        '贵金属':   {'technical_weight': 0.7, 'fundamental_weight': 0.8, 'chain_logic_weight': 0.5, 'macro_weight': 1.8},
        '油脂油料': {'technical_weight': 0.8, 'fundamental_weight': 1.4, 'chain_logic_weight': 1.2, 'macro_weight': 0.6},
        '谷物软商品': {'technical_weight': 0.7, 'fundamental_weight': 1.5, 'chain_logic_weight': 0.8, 'macro_weight': 0.5},
        '建材':     {'technical_weight': 1.1, 'fundamental_weight': 0.9, 'chain_logic_weight': 1.2, 'macro_weight': 1.0},
        '橡胶':     {'technical_weight': 1.0, 'fundamental_weight': 1.1, 'chain_logic_weight': 0.8, 'macro_weight': 0.7},
        '纸浆造纸': {'technical_weight': 1.0, 'fundamental_weight': 1.0, 'chain_logic_weight': 1.1, 'macro_weight': 0.6},
    },
}

# 兼容性别名
ADAPTIVE_WEIGHT_SYSTEM = CONFIG_MANAGER['adaptive_weights']
PRODUCT_THRESHOLDS = CONFIG_MANAGER['product_thresholds']
MARKET_STATE_SYSTEM = CONFIG_MANAGER['market_state']

# 产业链类型映射
CHAIN_TYPE_MAPPING = {
    '黑色系': 'industrial', '能源链': 'industrial', '聚酯链': 'industrial',
    '油化工': 'industrial', '煤化工': 'industrial',
    '有色金属': 'nonferrous', '有色': 'nonferrous', '贵金属': 'precious',
    '油脂油料': 'agricultural', '谷物软商品': 'agricultural',
    '建材': 'industrial', '橡胶': 'industrial', '纸浆造纸': 'industrial',
}

# 产业链阈值映射
CHAIN_THRESHOLD_MAPPING = {
    '黑色系': 'black', '能源链': 'energy', '聚酯链': 'energy',
    '油化工': 'energy', '煤化工': 'energy',
    '有色金属': 'nonferrous', '有色': 'nonferrous', '贵金属': 'precious',
    '油脂油料': 'agricultural', '谷物软商品': 'agricultural',
    '建材': 'nonferrous', '橡胶': 'nonferrous', '纸浆造纸': 'nonferrous',
}

# 指标参数配置
INDICATOR_CONFIG = {
    'MA':   {'periods': [5, 10, 20, 40, 60], 'weight': 30},
    'MACD': {'fast': 12, 'slow': 26, 'signal': 9, 'weight': 20},
    'RSI':  {'period': 14, 'overbought': 70, 'oversold': 30, 'weight': 10},
    'DMI':  {'period': 14, 'smooth': 6, 'weight': 20},
    'ATR':  {'period': 14, 'high_threshold': 3.0, 'low_threshold': 1.0, 'use_for_scoring': False},
    'VOLUME': {'obv_ma_period': 20, 'weight': 10},
    'PRICE_POSITION': {'ma_period': 20, 'weight': 15},
}


# ============================================================
# 工具函数
# ============================================================

def get_product_type(chain_name: str) -> str:
    """获取产业链品种类型。"""
    return CHAIN_TYPE_MAPPING.get(chain_name, 'industrial')


def get_product_thresholds(chain_name: str) -> dict:
    """获取品种特异性阈值。"""
    threshold_type = CHAIN_THRESHOLD_MAPPING.get(chain_name, 'default')
    return PRODUCT_THRESHOLDS.get(threshold_type, PRODUCT_THRESHOLDS['default'])


def get_adaptive_weights(product_type: str = 'industrial', market_state: str = 'trending') -> dict:
    """获取自适应权重。"""
    base_weights = ADAPTIVE_WEIGHT_SYSTEM['default_weights'].copy()

    state_factors = ADAPTIVE_WEIGHT_SYSTEM['market_state_factors'].get(market_state, {})
    for indicator, factor in state_factors.items():
        if indicator in base_weights:
            base_weights[indicator] *= factor

    type_factors = ADAPTIVE_WEIGHT_SYSTEM['product_type_factors'].get(product_type, {})
    for indicator, factor in type_factors.items():
        if indicator in base_weights:
            base_weights[indicator] *= factor

    total_weight = sum(base_weights.values())
    if total_weight > 0:
        for indicator in base_weights:
            base_weights[indicator] = (base_weights[indicator] / total_weight) * 100

    return base_weights


def calculate_position_size(confidence: str, volatility_state: str) -> str:
    """计算动态仓位。"""
    base = CONFIG_MANAGER['trading']['base_position']
    if confidence == '高':
        pos = base * 1.5
    elif confidence == '中':
        pos = base * 1.0
    else:
        pos = base * 0.5

    if volatility_state == 'high':
        pos *= 0.7
    elif volatility_state == 'low':
        pos *= 1.3

    pos = min(pos, CONFIG_MANAGER['trading']['max_position'])
    pos = max(pos, CONFIG_MANAGER['trading']['min_position'])
    return f"{pos:.1f}%"


def calculate_atr_stop_loss(current_price: float, atr_value: float, direction: str) -> float:
    """计算ATR动态止损。"""
    if atr_value > 0:
        mult = CONFIG_MANAGER['trading']['atr_multiplier']
        dist = atr_value * mult
        return current_price - dist if direction == 'BUY' else current_price + dist
    return current_price * 0.95 if direction == 'BUY' else current_price * 1.05


def get_chain_debate_weight(chain_name: str) -> dict:
    """获取产业链辩论权重。"""
    return CONFIG_MANAGER['chain_debate_weights'].get(
        chain_name,
        {'technical_weight': 1.0, 'fundamental_weight': 1.0, 'chain_logic_weight': 1.0, 'macro_weight': 1.0}
    )


def get_atr_adaptive_thresholds(chain_name: str, atr_pct: float) -> dict:
    """ATR自适应趋势阈值。"""
    chain_atr_factor = {
        '黑色系': 1.5, '能源链': 1.3, '聚酯链': 1.0, '油化工': 1.0,
        '煤化工': 1.1, '有色': 1.0, '贵金属': 0.6, '油脂油料': 1.2,
        '谷物软商品': 1.1, '建材': 1.2, '橡胶': 1.3, '纸浆造纸': 0.6,
    }
    factor = chain_atr_factor.get(chain_name, 1.0)
    if atr_pct > 3.0:
        factor *= 1.3
    elif atr_pct < 1.0:
        factor *= 0.7

    base = {'strong_bullish': 30, 'weak_bullish': 10, 'strong_bearish': -30, 'weak_bearish': -10}
    return {k: v * factor for k, v in base.items()}
