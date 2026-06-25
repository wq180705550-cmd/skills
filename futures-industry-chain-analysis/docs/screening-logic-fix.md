# 筛选逻辑修复报告

**日期**: 2026-06-24
**版本**: futures-industry-chain-analysis v2.9.1

---

## 问题诊断

### 用户反馈
1. **置信度过低仍被推荐**：生猪37%、花生32%低于40%阈值却仍被输出
2. **逻辑矛盾**：市场整体偏空，但推荐的多头（2个）比空头（1个）更多

### 根因分析

| Bug | 位置 | 原因 |
|-----|------|------|
| 置信度阈值被绕过 | run_pipeline.py:120 | `generate_trade_plan`返回HOLD后，用自己的置信度计算重新判断，两个计算方式不一致 |
| 市场偏空时多头未惩罚 | run_pipeline.py:101 | 只有-10%的产业链背离调整，力度不够 |
| 辩论HOLD视为一致 | run_pipeline.py:88 | `debate_decision['verdict'] in ('BUY', 'HOLD')` 导致HOLD被视为一致 |

---

## 修复内容

### 1. run_pipeline.py

#### 1.1 移除绕过置信度阈值的逻辑
```python
# 修复前：绕过置信度检查
if trade_plan['decision'] == 'HOLD' and confidence >= 0.4:
    # 手动构建交易方案...

# 修复后：严格执行
if trade_plan['decision'] == 'HOLD':
    continue  # 直接跳过
```

#### 1.2 辩论一致性检查
```python
# 修复前：HOLD视为一致
debate_aligned = (
    (signal_direction == 'BUY' and debate_decision['verdict'] in ('BUY', 'HOLD')) or
    (signal_direction == 'SELL' and debate_decision['verdict'] in ('SELL', 'HOLD'))
)

# 修复后：HOLD视为中性偏负
debate_aligned = (
    (signal_direction == 'BUY' and debate_decision['verdict'] == 'BUY') or
    (signal_direction == 'SELL' and debate_decision['verdict'] == 'SELL')
)
debate_neutral = debate_decision['verdict'] == 'HOLD'

if debate_aligned:
    pass  # 一致，不调整
elif debate_neutral:
    confidence *= 0.85  # HOLD中性结果，轻微降权
else:
    confidence *= 0.6  # 辩论结果与信号方向矛盾，大幅降权
```

#### 1.3 市场环境惩罚
```python
# 新增：市场整体偏空时，多头信号需要更高置信度
market_bearish = sum(1 for cr in chain_results.values() 
                     if '空' in cr.get('overall_trend', '')) > len(chain_results) * 0.6
if market_bearish and signal_direction == 'BUY':
    confidence *= 0.8  # 偏空市场做多，额外惩罚20%
```

#### 1.4 二次过滤
```python
# 新增：调整后置信度仍需 >= 0.4
if confidence < 0.4:
    continue
```

### 2. screen.py

#### 2.1 市场环境判断
```python
# 新增：判断市场整体环境
buy_count = sum(1 for s in symbols if s.get('trend', {}).get('score', 0) > 20)
sell_count = sum(1 for s in symbols if s.get('trend', {}).get('score', 0) < -20)
market_bearish = sell_count > buy_count * 1.5
market_bullish = buy_count > sell_count * 1.5
```

#### 2.2 动态共振度阈值
```python
# 新增：市场环境过滤
direction = 'BUY' if score > 0 else 'SELL'
required_resonance = min_resonance
if market_bearish and direction == 'BUY':
    required_resonance = 0.6  # 偏空市场做多需要60%共振度
elif market_bullish and direction == 'SELL':
    required_resonance = 0.6  # 偏多市场做空需要60%共振度

if resonance['ratio'] < required_resonance:
    continue
```

---

## 验证结果

### 筛选结果对比

| 指标 | 修复前 | 修复后 | 变化 |
|------|--------|--------|------|
| 扫描品种 | 67 | 67 | - |
| 候选信号 | 33 | 30 | -9% |
| 有效机会 | 3 | 1 | -67% |
| 做多机会 | 2 | 0 | -100% |
| 做空机会 | 1 | 1 | - |

### 具体品种对比

| 品种 | 方向 | 修复前置信度 | 修复后置信度 | 状态 |
|------|------|-------------|-------------|------|
| 豆粕(m) | 做空 | 66% | **50%** | ✅ 保留（置信度更准确） |
| 生猪(lh) | 做多 | 37% | - | ❌ 被过滤（市场偏空惩罚+置信度不足） |
| 花生(PK) | 做多 | 32% | - | ❌ 被过滤（置信度不足） |

### 测试结果

```
tests/test_screen.py::TestDetectTrendStage::test_early_bull PASSED
tests/test_screen.py::TestDetectTrendStage::test_exhausted_bear PASSED
tests/test_screen.py::TestCountResonance::test_strong_bull_resonance PASSED
tests/test_screen.py::TestCountResonance::test_weak_resonance PASSED
tests/test_screen.py::TestGetChainForSymbol::test_black_chain PASSED
tests/test_screen.py::TestGetChainForSymbol::test_energy_chain PASSED
tests/test_screen.py::TestGetChainForSymbol::test_new_symbols PASSED
tests/test_screen.py::TestChainVerification::test_aligned_signal PASSED
tests/test_screen.py::TestChainVerification::test_divergent_signal PASSED
tests/test_screen.py::TestScreenSignalsMarketFilter::test_balanced_market_normal_filtering PASSED
tests/test_screen.py::TestScreenSignalsMarketFilter::test_bearish_market_filters_weak_buy_signals PASSED

============================== 11 passed in 0.29s ==============================
```

---

## 设计原则强化

1. **宁缺毋滥**：宁可没有机会，也不推荐低置信度信号
2. **市场一致性**：市场整体偏空时，多头信号需要更高置信度才能通过
3. **阈值严格执行**：不再有任何绕过置信度阈值的逻辑
4. **动态过滤**：根据市场环境动态调整共振度阈值

---

## 技能更新

- **版本**: v2.9.0 → v2.9.1
- **测试**: 9个 → 11个（新增市场环境过滤测试）
- **SKILL.md**: 已更新changelog
