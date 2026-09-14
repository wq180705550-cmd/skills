---
name: quant-data-bug-triage
description: 量化/数据管道中「取数失败或数值异常」的归因诊断流程。当代码出现空值、全0、恒真判断、信号全量降级，且日志把原因指向数据源时使用。核心方法是先用最小脚本实测数据源，区分「数据源真故障」与「自身代码 bug（键名/量纲/字段名）」。触发词：数据源失败、取不到数据、返回非JSON、ref_price为空、量能异常、全0、恒判量增、回测失真、字段名错误。
agent_created: true
---

# 量化数据管道 Bug 归因诊断

## 何时使用

出现以下任一症状：

- 报告/信号里某个关键字段恒为 `None` 或 `0`
- 判断逻辑"恒真"或"恒假"（如量增/量缩永远只出一侧）
- 日志报 `Expecting value: line 1 column 1`、`JSONDecodeError`、`KeyError`
- 多个标的输出完全相同的结论
- 信号全量降级为 HOLD / 空仓

## 核心原则

> **日志把原因指向数据源时，不要相信它。先用最小脚本实测。**

实践中，被归因为"数据源故障"的问题里，**大部分是自身代码的字段名或量纲错误**。
`except` 吞异常 + `logger.warning` 的组合会让自身 bug 伪装成外部故障。

## 四步诊断法

### 第 1 步：最小脚本实测数据源

脱离业务代码，用最简请求直接打接口，打印原始响应：

```python
import requests
r = requests.get(URL, params=P, timeout=10, proxies={}, headers=H)
print(r.status_code, len(r.text))
print(repr(r.text[:200]))          # 看原始文本，不要只看 .json()
try:
    d = r.json(); print('JSON OK, rows =', len(d))
    if isinstance(d, list) and d: print('keys =', list(d[0].keys()))
except Exception as e:
    print('JSON FAIL:', type(e).__name__, e)
```

**判定**：
- 200 + 合法 JSON → **数据源正常，问题在自己的代码**，进入第 2 步
- 非 200 / 非 JSON → 才是真数据源问题，进入第 4 步

### 第 2 步：核对字段名（最高频根因）

拿第 1 步打印的真实 `keys()`，逐字比对代码里的取值语句：

```python
# 常见错误：字段名凭记忆写
row.get("name")       # 实际没有这个键 → None
row.get("current")    # 实际没有这个键 → None

# 正确做法：用实测到的真实字段名
row.get("index_name")
row.get("current_price")
```

**排查要点**：`dict.get()` 缺失键返回 `None` 而不报错，是最隐蔽的失败方式。
对所有 `get()` 取值，都要确认键名在真实响应里存在。

### 第 3 步：核对量纲与单位

同一业务指标从不同数据源取来时，单位常常不同：

| 易混概念 | 常见单位 | 量级差异 |
|---|---|---|
| 成交量 vs 成交额 | 股 vs 元 | 约 10 倍（取决于股价） |
| 金额 元 vs 万元 vs 亿元 | — | 1e4 / 1e8 |
| 百分比 vs 小数 | % vs 0~1 | 100 倍 |

**验证方法**：算比值并检查是否落在合理区间。

```python
ratio = current_vol / ma5_vol
assert 0.2 < ratio < 5.0, f"比值 {ratio:.2f} 超出合理区间，疑似量纲错配"
```

**典型症状**：错配后比值恒 >10（或恒 <0.1），判断逻辑退化为单向输出（恒判"量增"）。

### 第 4 步：确属数据源问题时的处理

1. **加重试**：间歇性失败（并发限流）用 2~3 次重试可解决
2. **兜底可用性标记**：降级时在输出中记录来源，例如 `vol_source: "unavailable"`，
   让问题可见而非静默为 0
3. **保留原始响应**：失败时记录 `resp.text[:200]`，便于后续定位

## 关键防御措施

### 输出里带上数据来源标记

```python
if current_vol <= 0:
    current_vol = quote.get("amount", 0) / 1e8
    vol_source = "fallback_amount" if current_vol > 0 else "unavailable"
else:
    vol_source = "primary"
```

这比"静默返回 0"强得多——问题会在输出里暴露，而不是变成看似正常的错误结论。

### 为字段名和量纲写回归测试

修好之后必须加测试锁定，防止重蹈覆辙：

```python
def test_uses_real_field_names():
    """回归保护：字段名必须与真实响应一致。"""
    real_shape = {"index_analysis": [{"index_name": "沪深300", "current_price": 4498.58}]}
    s = build(real_shape)
    assert s["ref_price"] == pytest.approx(4498.58)

def test_volume_source_is_consistent():
    """量能比较必须同源同量纲。"""
    for w in get_warnings():
        assert w["vol_source"] == "primary"
```

测试数据要**粘贴真实响应**，不要手写猜测的字段名——否则测试会跟着错误一起通过。

## 反面模式清单

| 反面模式 | 后果 |
|---|---|
| 用 `dict.get()` 却不验证键名存在 | 静默返回 None，一路传到底 |
| 用 `except Exception` 吞掉后返回默认值 | 自身 bug 伪装成数据源故障 |
| 手写测试数据的字段名（而非粘贴真实响应） | 测试通过但线上失败 |
| 跨数据源比较同名字段（volume/amount） | 量纲错配，逻辑退化 |
| 看到"多个标的结果相同"就断定 bug | 可能是真实行情（需查数值确认） |

## 最后一条

**异常日志会撒谎。** `logger.warning("获取XXX失败")` 只说明 except 被触发，
不说明根因在外网。先实测，再归因。
