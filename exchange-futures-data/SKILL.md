---
name: exchange-futures-data
description: 中国五大期货交易所（大商所/上期所/郑商所/中金所/广期所）官方数据采集与持久化。当用户需要获取期货日线行情数据、批量采集历史数据、或需要交易所官方权威数据源时使用。支持自动缓存到DuckDB，避免重复获取。
agent_created: true
---

# 交易所官方期货数据采集

## 概述

从中国五大期货交易所官方API采集日线行情数据，自动持久化到DuckDB数据库。数据源最权威，无爬虫合规风险。每次获取数据时自动检查缓存，已有数据直接读取，新数据自动入库。

### 适用场景
- 获取指定交易日各交易所全部品种的日线行情
- 批量采集历史日线数据
- 作为期货产业链分析的数据源（最高优先级）
- 验证其他数据源（TqSdk、AKShare）的数据准确性

## 支持的交易所

| 交易所 | 代码 | 数据格式 | 覆盖品种 |
|--------|------|---------|----------|
| 大连商品交易所 | DCE | TSV | 豆粕、豆油、铁矿石、焦炭、焦煤、鸡蛋等 |
| 上海期货交易所 | SHFE | JSON | 螺纹钢、铜、铝、锌、橡胶、燃料油等（含上期能源） |
| 郑州商品交易所 | CZCE | HTML | PTA、甲醇、白糖、棉花、纯碱、尿素等 |
| 中国金融期货交易所 | CFFEX | CSV | 沪深300、中证500、中证1000、国债等（股指+利率） |
| 广州期货交易所 | GFEX | JSON | 碳酸锂、工业硅、多晶硅 |

## 硬规则（必须遵守）

1. **数据真实性**：禁止编造价格/成交量数据，数据必须来自交易所官方API响应
2. **时效性**：行情数据必须是当天或最近交易日的实时数据，延迟不超过1个交易日
3. **可追溯**：每行数据标注来源字段（`source`），如 `DCE官方API`
4. **先查缓存**：每次获取数据前必须检查DuckDB缓存（`use_cache=True`默认）
5. **完整性校验**：`high >= low`，价格和量为非负数，空值自动标记
6. **错误处理**：API请求失败自动重试3次（间隔2秒，指数退避1.5x）
7. **交易日校验**：非交易日（周末+法定节假日）不发起API请求
8. **导入可验**：`from scripts.exchange_data_collector import ExchangeDataCollector` 必须在技能根目录下执行

## 快速开始

### 1. 导入采集器（必须在skill根目录）

```bash
cd ~/.workbuddy/skills/exchange-futures-data
```

```python
from scripts.exchange_data_collector import ExchangeDataCollector

collector = ExchangeDataCollector()
```

### 2. 获取最近交易日数据

```python
trade_date = collector.get_latest_trading_day()
df = collector.get_all_exchange_data(trade_date)
```

### 3. 指定日期 + 禁用缓存

```python
df = collector.get_all_exchange_data('20260624', use_cache=False)
```

### 4. 批量采集历史数据

```python
collector.batch_collect('20260601', '20260624')
```

### 5. 查询缓存状态

```python
total = collector.get_cached_count()
cached_dates = collector.get_cached_dates()
print(f"已缓存 {total} 条记录, {len(cached_dates)} 个交易日")
```

## 数据持久化（DuckDB）

所有采集的数据自动存储在DuckDB数据库中。连接复用（无重复创建/销毁开销），批量插入（避免逐行SELECT）。

### 数据库位置

`data/exchange_futures_data.duckdb`（运行时自动创建）

### 数据表结构

```sql
CREATE TABLE daily_data (
    exchange       VARCHAR,       -- 交易所代码: DCE/SHFE/CZCE/CFFEX/GFEX
    symbol         VARCHAR,       -- 合约代码
    trade_date     VARCHAR,       -- 交易日期 YYYYMMDD
    open           DOUBLE,        -- 开盘价
    high           DOUBLE,        -- 最高价
    low            DOUBLE,        -- 最低价
    close          DOUBLE,        -- 收盘价
    settle         DOUBLE,        -- 结算价
    volume         BIGINT,        -- 成交量
    open_interest  BIGINT,        -- 持仓量
    turnover       DOUBLE,        -- 成交额
    source         VARCHAR,       -- 数据来源: DCE官方API / SHFE官方API 等
    created_at     TIMESTAMP,     -- 入库时间
    PRIMARY KEY (exchange, symbol, trade_date)
)
```

### 查询示例

```python
import duckdb

conn = duckdb.connect('data/exchange_futures_data.duckdb')

# 查询指定日期数据
df = conn.execute("SELECT * FROM daily_data WHERE trade_date = '20260624'").fetchdf()

# 查询某品种历史数据
df = conn.execute("""
    SELECT * FROM daily_data
    WHERE symbol LIKE 'm%'
    ORDER BY trade_date DESC
""").fetchdf()

# 查看已缓存日期
dates = conn.execute("""
    SELECT DISTINCT trade_date FROM daily_data
    ORDER BY trade_date DESC
""").fetchall()

conn.close()
```

## 各交易所API详情（详见 references/exchange_api_config.json）

| 交易所 | 代码 | 端点格式 | 说明 |
|--------|------|---------|------|
| 大商所 | DCE | POST .../exportDayQuotesChData.html | TSV，月份0起 |
| 上期所 | SHFE | GET .../kx{YYYYMMDD}.dat | JSON |
| 郑商所 | CZCE | GET .../FutureDataDaily.htm | HTML(>20151111) |
| 中金所 | CFFEX | GET .../lsjy.dll | CSV |
| 广期所 | GFEX | GET .../rihq/{YYYYMMDD}.js | JSON

## 跨技能引用

在其他技能中引入交易所数据（必须使用绝对路径）：

```python
import sys
import os
sys.path.insert(0, os.path.expanduser('~/.workbuddy/skills/exchange-futures-data'))
from scripts.exchange_data_collector import ExchangeDataCollector

collector = ExchangeDataCollector()
df = collector.get_all_exchange_data('20260624')
```

## 已知限制与反幻觉说明

1. **API可用性**: 交易所API可能在休市后更新，部分交易所周末不返回数据
2. **节假日**: 内置2026年已知节假日列表，但调休上班日会正常交易
3. **CFETS异常**: 中金所接口的`lsjy.dll`路径格式未经实盘验证，可能需要调整
4. **成交额缺失**: 部分交易所（如CZCE旧版）可能不返回`turnover`字段
5. **数据延迟**: 交易所日线通常在收盘后30分钟~2小时内发布
6. **信号降级**: 所有从API获取的数据都标注 `source` 字段，不信任任何硬编码预制数据

## 数据真实性验证

每次采集后自动执行：
1. `high >= low` 校正（若违反则自动互换）
2. 成交量/持仓量/成交额非负检查
3. 符号/价格非空检查
4. 无效记录自动丢弃（不存入DuckDB）

## 测试

```bash
# 在skill根目录运行
cd ~/.workbuddy/skills/exchange-futures-data
python -m scripts.test_exchange_data_collector
```

## 参考文档

- `references/exchange_api_config.json` — 各交易所API端点详细配置，可加载到上下文中参考

## 目录结构

```
exchange-futures-data/
├── SKILL.md                            # 主技能文档
├── scripts/
│   ├── exchange_data_collector.py      # 交易所数据采集器 v3.0（连接复用+重试+校验）
│   └── test_exchange_data_collector.py # 硬规则测试套件（19项硬规则）
├── references/
│   └── exchange_api_config.json        # 交易所API配置（供AI加载参考）
└── data/                               # 运行时自动创建
    └── exchange_futures_data.duckdb    # DuckDB持久化数据库（运行时）
```

> `data/` 目录和DuckDB数据库由代码在运行时自动创建，skill中不预制。
