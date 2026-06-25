#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
产业链分析模块
基于产业链的期货分析，包括产业链映射、上下游关系、供需分析等
"""

import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class IndustryChainAnalyzer:
    """产业链分析器"""
    
    def __init__(self):
        """初始化产业链分析器"""
        # 定义产业链映射关系
        self.industry_chains = {
            # 黑色系产业链
            'black': {
                'name': '黑色系产业链',
                'products': {
                    'i': {'name': '铁矿石', 'exchange': 'DCE', 'position': '上游原料'},
                    'j': {'name': '焦炭', 'exchange': 'DCE', 'position': '中游辅料'},
                    'jm': {'name': '焦煤', 'exchange': 'DCE', 'position': '上游原料'},
                    'rb': {'name': '螺纹钢', 'exchange': 'SHFE', 'position': '下游成品'},
                    'hc': {'name': '热卷', 'exchange': 'SHFE', 'position': '下游成品'},
                    'SF': {'name': '硅铁', 'exchange': 'CZCE', 'position': '中游辅料'},
                    'SM': {'name': '锰硅', 'exchange': 'CZCE', 'position': '中游辅料'},
                },
                'flow': '焦煤→焦炭→铁矿石+焦炭→螺纹钢/热卷',
                'key_relationships': [
                    ('i', 'rb', '铁矿石是螺纹钢的主要原料'),
                    ('j', 'rb', '焦炭是高炉炼钢的辅料'),
                    ('jm', 'j', '焦煤是焦炭的原料'),
                ],
            },
            # 能源链
            'energy': {
                'name': '能源链',
                'products': {
                    'sc': {'name': '原油', 'exchange': 'INE', 'position': '上游原料'},
                    'lu': {'name': '低硫燃料油', 'exchange': 'INE', 'position': '中游产品'},
                    'fu': {'name': '燃料油', 'exchange': 'SHFE', 'position': '中游产品'},
                    'bu': {'name': '沥青', 'exchange': 'SHFE', 'position': '中游产品'},
                    'pg': {'name': 'LPG', 'exchange': 'DCE', 'position': '中游产品'},
                },
                'flow': '原油→燃油/沥青/LPG',
                'key_relationships': [
                    ('sc', 'lu', '原油是低硫燃料油的原料'),
                    ('sc', 'fu', '原油是燃料油的原料'),
                    ('sc', 'bu', '原油是沥青的原料'),
                    ('sc', 'pg', '原油是LPG的原料'),
                ],
            },
            # 聚酯链
            'polyester': {
                'name': '聚酯链',
                'products': {
                    'PX': {'name': '对二甲苯', 'exchange': 'CZCE', 'position': '上游原料'},
                    'TA': {'name': 'PTA', 'exchange': 'CZCE', 'position': '中游产品'},
                    'PF': {'name': '短纤', 'exchange': 'CZCE', 'position': '下游产品'},
                    'PR': {'name': '瓶片', 'exchange': 'CZCE', 'position': '下游产品'},
                },
                'flow': 'PX→PTA→短纤/瓶片',
                'key_relationships': [
                    ('PX', 'TA', 'PX是PTA的原料'),
                    ('TA', 'PF', 'PTA是短纤的原料'),
                    ('TA', 'PR', 'PTA是瓶片的原料'),
                ],
            },
            # 油化工
            'oil_chemical': {
                'name': '油化工',
                'products': {
                    'eg': {'name': '乙二醇', 'exchange': 'DCE', 'position': '中游产品'},
                    'eb': {'name': '苯乙烯', 'exchange': 'DCE', 'position': '中游产品'},
                    'v': {'name': 'PVC', 'exchange': 'DCE', 'position': '下游产品'},
                    'pp': {'name': 'PP', 'exchange': 'DCE', 'position': '下游产品'},
                    'l': {'name': '塑料', 'exchange': 'DCE', 'position': '下游产品'},
                    'PL': {'name': '丙烯', 'exchange': 'CZCE', 'position': '中游产品'},
                    'ps': {'name': '聚苯乙烯', 'exchange': 'DCE', 'position': '下游产品'},
                    'bz': {'name': '纯苯', 'exchange': 'CZCE', 'position': '中游产品'},
                },
                'flow': '原油→乙烯/苯→PP/PVC/PE/PS/苯乙烯',
                'key_relationships': [
                    ('sc', 'eg', '原油是乙二醇的原料之一'),
                    ('sc', 'eb', '原油是苯乙烯的原料'),
                    ('PL', 'pp', '丙烯是PP的原料'),
                    ('bz', 'eb', '纯苯是苯乙烯的原料'),
                ],
            },
            # 煤化工
            'coal_chemical': {
                'name': '煤化工',
                'products': {
                    'MA': {'name': '甲醇', 'exchange': 'CZCE', 'position': '中游产品'},
                    'SH': {'name': '烧碱', 'exchange': 'CZCE', 'position': '下游产品'},
                },
                'flow': '煤→甲醇→MTO→烯烃',
                'key_relationships': [
                    ('MA', 'SH', '甲醇和烧碱在氯碱工业中有关系'),
                ],
            },
            # 有色金属产业链
            'nonferrous': {
                'name': '有色金属产业链',
                'products': {
                    'cu': {'name': '铜', 'exchange': 'SHFE', 'position': '核心品种'},
                    'al': {'name': '铝', 'exchange': 'SHFE', 'position': '核心品种'},
                    'zn': {'name': '锌', 'exchange': 'SHFE', 'position': '核心品种'},
                    'pb': {'name': '铅', 'exchange': 'SHFE', 'position': '核心品种'},
                    'ni': {'name': '镍', 'exchange': 'SHFE', 'position': '核心品种'},
                    'sn': {'name': '锡', 'exchange': 'SHFE', 'position': '核心品种'},
                    'ao': {'name': '氧化铝', 'exchange': 'SHFE', 'position': '上游原料'},
                    'bc': {'name': '国际铜', 'exchange': 'INE', 'position': '核心品种'},
                    'si': {'name': '工业硅', 'exchange': 'GFEX', 'position': '上游原料'},
                    'SS': {'name': '不锈钢', 'exchange': 'SHFE', 'position': '下游成品'},
                    'ad': {'name': '铝合金', 'exchange': 'SHFE', 'position': '下游成品'},
                },
                'flow': '氧化铝→铝/铝合金，镍→不锈钢',
                'key_relationships': [
                    ('ao', 'al', '氧化铝是电解铝的原料'),
                    ('al', 'ad', '铝合金和铝走势高度一致'),
                    ('ni', 'SS', '不锈钢的主要原料是镍'),
                ],
            },
            # 贵金属
            'precious': {
                'name': '贵金属',
                'products': {
                    'au': {'name': '黄金', 'exchange': 'SHFE', 'position': '核心品种'},
                    'ag': {'name': '白银', 'exchange': 'SHFE', 'position': '核心品种'},
                    'pt': {'name': '铂', 'exchange': 'SHFE', 'position': '核心品种'},
                },
                'flow': '黄金-白银-铂金比价',
                'key_relationships': [
                    ('au', 'ag', '黄金和白银有比价关系'),
                    ('au', 'pt', '黄金和铂金有比价关系'),
                ],
            },
            # 油脂油料产业链
            'oil_oilseed': {
                'name': '油脂油料产业链',
                'products': {
                    'a': {'name': '豆一', 'exchange': 'DCE', 'position': '上游原料'},
                    'b': {'name': '豆二', 'exchange': 'DCE', 'position': '上游原料'},
                    'm': {'name': '豆粕', 'exchange': 'DCE', 'position': '压榨产品'},
                    'y': {'name': '豆油', 'exchange': 'DCE', 'position': '压榨产品'},
                    'p': {'name': '棕榈油', 'exchange': 'DCE', 'position': '油脂'},
                    'OI': {'name': '菜油', 'exchange': 'CZCE', 'position': '油脂'},
                    'RM': {'name': '菜粕', 'exchange': 'CZCE', 'position': '压榨产品'},
                    'PK': {'name': '花生', 'exchange': 'CZCE', 'position': '原料'},
                },
                'flow': '大豆→豆粕+豆油，油菜籽→菜油+菜粕',
                'key_relationships': [
                    ('a', 'm', '大豆压榨产生豆粕'),
                    ('a', 'y', '大豆压榨产生豆油'),
                    ('m', 'RM', '豆粕和菜粕在饲料中有替代关系'),
                    ('y', 'p', '豆油和棕榈油在食用油中有替代关系'),
                    ('y', 'OI', '豆油和菜油在食用油中有替代关系'),
                ],
            },
            # 谷物软商品产业链
            'grain': {
                'name': '谷物软商品产业链',
                'products': {
                    'c': {'name': '玉米', 'exchange': 'DCE', 'position': '上游原料'},
                    'cs': {'name': '淀粉', 'exchange': 'DCE', 'position': '加工产品'},
                    'SR': {'name': '白糖', 'exchange': 'CZCE', 'position': '原料'},
                    'CF': {'name': '棉花', 'exchange': 'CZCE', 'position': '上游原料'},
                    'CY': {'name': '棉纱', 'exchange': 'CZCE', 'position': '下游产品'},
                    'jd': {'name': '鸡蛋', 'exchange': 'DCE', 'position': '终端产品'},
                    'lh': {'name': '生猪', 'exchange': 'DCE', 'position': '终端产品'},
                    'AP': {'name': '苹果', 'exchange': 'CZCE', 'position': '终端产品'},
                    'CJ': {'name': '红枣', 'exchange': 'CZCE', 'position': '终端产品'},
                    'rr': {'name': '粳米', 'exchange': 'DCE', 'position': '终端产品'},
                },
                'flow': '玉米→淀粉，棉花→棉纱',
                'key_relationships': [
                    ('c', 'cs', '玉米加工产生淀粉'),
                    ('CF', 'CY', '棉花是棉纱的原料'),
                ],
            },
            # 建材产业链
            'building': {
                'name': '建材产业链',
                'products': {
                    'FG': {'name': '玻璃', 'exchange': 'CZCE', 'position': '下游产品'},
                    'SA': {'name': '纯碱', 'exchange': 'CZCE', 'position': '上游原料'},
                    'UR': {'name': '尿素', 'exchange': 'CZCE', 'position': '原料'},
                },
                'flow': '纯碱→玻璃，尿素→化肥',
                'key_relationships': [
                    ('SA', 'FG', '纯碱是玻璃的原料'),
                ],
            },
            # 橡胶产业链
            'rubber': {
                'name': '橡胶产业链',
                'products': {
                    'ru': {'name': '天然橡胶', 'exchange': 'SHFE', 'position': '原料'},
                    'nr': {'name': '20号胶', 'exchange': 'INE', 'position': '原料'},
                    'br': {'name': '丁二烯橡胶', 'exchange': 'SHFE', 'position': '原料'},
                },
                'flow': '天然橡胶/合成橡胶→轮胎',
                'key_relationships': [
                    ('ru', 'nr', '天然橡胶和20号胶高度相关'),
                    ('ru', 'br', '天然橡胶和合成橡胶有替代关系'),
                ],
            },
            # 纸浆造纸产业链
            'paper': {
                'name': '纸浆造纸产业链',
                'products': {
                    'sp': {'name': '纸浆', 'exchange': 'SHFE', 'position': '上游原料'},
                    'op': {'name': '双胶纸', 'exchange': 'SHFE', 'position': '下游产品'},
                },
                'flow': '纸浆→纸张',
                'key_relationships': [
                    ('sp', 'op', '纸浆是双胶纸的原料'),
                ],
            },
        }
        
        logger.info(f"初始化产业链分析器，共{len(self.industry_chains)}个产业链")
    
    def get_industry_chain(self, product_id: str) -> Optional[Dict[str, Any]]:
        """获取品种所属的产业链
        
        Args:
            product_id: 品种代码（如rb, i, sc等）
            
        Returns:
            产业链信息
        """
        for chain_id, chain_info in self.industry_chains.items():
            if product_id in chain_info['products']:
                return {
                    'chain_id': chain_id,
                    'chain_name': chain_info['name'],
                    'product_info': chain_info['products'][product_id],
                    'products': chain_info['products'],
                    'flow': chain_info['flow'],
                    'key_relationships': chain_info['key_relationships'],
                }
        
        return None
    
    def get_related_products(self, product_id: str) -> List[Dict[str, Any]]:
        """获取相关品种
        
        Args:
            product_id: 品种代码
            
        Returns:
            相关品种列表
        """
        chain_info = self.get_industry_chain(product_id)
        if not chain_info:
            return []
        
        related = []
        for rel in chain_info['key_relationships']:
            if product_id in rel[:2]:
                other_product = rel[0] if rel[1] == product_id else rel[1]
                if other_product in chain_info['products']:
                    related.append({
                        'product_id': other_product,
                        'product_info': chain_info['products'][other_product],
                        'relationship': rel[2],
                    })
        
        return related
    
    def analyze_industry_chain_impact(self, product_id: str, 
                                      price_change: float,
                                      market_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析产业链影响
        
        Args:
            product_id: 品种代码
            price_change: 价格变动（百分比）
            market_data: 市场数据
            
        Returns:
            产业链影响分析
        """
        chain_info = self.get_industry_chain(product_id)
        if not chain_info:
            return {
                'product_id': product_id,
                'error': '未找到产业链信息',
            }
        
        analysis = {
            'product_id': product_id,
            'chain_name': chain_info['chain_name'],
            'product_position': chain_info['product_info']['position'],
            'price_change': price_change,
            'upstream_impact': [],
            'downstream_impact': [],
            'substitution_effect': [],
            'analysis_summary': '',
        }
        
        # 分析上下游影响
        for rel in chain_info['key_relationships']:
            if product_id == rel[0]:  # 当前品种是上游
                analysis['downstream_impact'].append({
                    'product_id': rel[1],
                    'relationship': rel[2],
                    'impact': '价格上升可能推高下游成本',
                })
            elif product_id == rel[1]:  # 当前品种是下游
                analysis['upstream_impact'].append({
                    'product_id': rel[0],
                    'relationship': rel[2],
                    'impact': '价格上升可能受上游成本推动',
                })
        
        # 生成分析摘要
        if price_change > 0:
            analysis['analysis_summary'] = f"{chain_info['product_info']['name']}价格上涨{price_change:.2f}%"
        else:
            analysis['analysis_summary'] = f"{chain_info['product_info']['name']}价格下跌{abs(price_change):.2f}%"
        
        if analysis['upstream_impact']:
            analysis['analysis_summary'] += "，关注上游原料成本变化"
        
        if analysis['downstream_impact']:
            analysis['analysis_summary'] += "，可能影响下游产品成本"
        
        return analysis
    
    def get_chain_products(self, chain_id: str) -> Dict[str, Any]:
        """获取产业链所有品种
        
        Args:
            chain_id: 产业链ID
            
        Returns:
            产业链品种信息
        """
        if chain_id not in self.industry_chains:
            return {'error': f'未找到产业链: {chain_id}'}
        
        chain = self.industry_chains[chain_id]
        return {
            'chain_id': chain_id,
            'chain_name': chain['name'],
            'products': chain['products'],
            'flow': chain['flow'],
        }
