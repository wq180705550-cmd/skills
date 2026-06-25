#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交易所官方数据采集模块 — 转发层

**核心实现在独立Skill中：exchange-futures-data**

本文件作为转发器，将调用转发到独立Skill的exchange_data_collector模块。
修复和升级请修改独立Skill中的对应文件。

独立Skill路径: ~/.workbuddy/skills/exchange-futures-data/
"""

import os
import sys
import warnings

# 指向独立Skill中核心模块
SKILL_PATH = os.path.expanduser(
    '~/.workbuddy/skills/exchange-futures-data/scripts'
)

if os.path.exists(SKILL_PATH):
    sys.path.insert(0, os.path.dirname(SKILL_PATH))
    from scripts.exchange_data_collector import ExchangeDataCollector
else:
    warnings.warn(
        "独立Skill exchange-futures-data 未安装，请先安装："
        "~/.workbuddy/skills/exchange-futures-data/"
    )
    # 如果独立Skill不存在，抛ImportError
    raise ImportError("exchange-futures-data skill not found")
