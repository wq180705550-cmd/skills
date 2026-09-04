---
name: macro-quarterly-report
description: 从宏观指标体系生成近两年季度同比/环比分析报告（折线图+柱状图 HTML）。数据源为 westock-data CLI 宏观接口（真实数据，禁止编造）。适用触发词：月度宏观数据、宏观季度报告、宏观数据抓取、季度同比环比分析、每月10号宏观任务。不与任何源文件数据对比，窗口自动滚动。
---

# 宏观季度报告生成

**指标体系来源**：《转向：力度与后续》（徐远 2024.10.07）的分析框架——需求三驾马车 / 生产与利润 / 物价 / 货币金融 / 财政 / 景气与就业 / 居民收入。

**参考实现**（完整可运行代码）：`C:\Users\Administrator\WorkBuddy\2026-08-29-14-30-14\月度宏观数据\` 目录下的 `build_report.py`、`update_report.sh`。首次在新工作空间使用时，直接复制这两个文件再按需调整指标表。

---

## 工作流

### 1. 抓取原始数据（westock-data CLI，月度序列 2023 年起）

```bash
cd ~/.workbuddy/skills/westock-data
NODE="C:/Users/Administrator/.workbuddy/binaries/node/versions/22.22.2-2/node.exe"
for ind in gdp cpi_ppi pmi consumption investment export valueadded profit \
           financing fiscal employment disposable_income prosperity yield_curve fundquantity; do
  "$NODE" scripts/index.js macro indicator "$ind" --start 2023 --end $(date +%Y) --raw > "raw/$ind.json"
done
```

- 输出落盘为 JSON（sections 数组），**不要直接打印到上下文**——单响应极大会撑爆窗口。
- 每条记录含日期键（如 `CPI_END_DATE`，格式 yyyymmdd）与指标键（如 `CPI_CPI_YOY`）。字段名因指标而异，先跑一次探测脚本确认。

### 2. 月度→季度聚合口径（build_report.py 的 INDICATORS 表）

| 类型 | 聚合 | 示例 |
|---|---|---|
| 累计同比类 | 取季末值（agg=last） | 投资、工业增加值、利润、财政、M1/M2、社融 |
| 当月同比/指数类 | 季内 3 月算术平均（agg=mean） | 社零、CPI、PPI、PMI、失业率 |
| 日频类 | 先取月末值，再季内平均 | 10 年期国债收益率 |
| 本身季频 | 直接取值 | GDP、人均收支、企业景气指数 |

同比 = 本期 − 上年同季；环比 = 本期 − 上季。**一律百分点差，不做百分比换算。**

### 3. 报告生成（零依赖 Python + 内嵌 SVG）

- 每指标 2 图：季度走势折线 + 同比/环比双柱状。纯 SVG 手绘（nice_ticks 刻度算法），不依赖任何图表库。
- 结构：KPI 概览卡 → 全指标总览表 → 7 板块明细（每组综合判断 + 明细表 + 逐指标图表）→ 方法论。
- 涨红跌绿（A股惯例），`+`/`-` 着色区分。

### 4. 窗口与"最后完整季度"判定（关键踩坑）

```python
cnt = {q: sum(1 for v in series.values() if q in v) for q in sorted_q}
full = max(cnt.values())
last_q = max((q for q in sorted_q if cnt[q] >= full - 1), key=sk)  # 允许缺1项
```

- ❌ 60% 覆盖阈值 → 会把发布中的当季（如 9 月初的 Q3）当完整季度
- ❌ `cnt[q] == full` → 数据源单指标缺口会让窗口过度回退一个季度
- ✅ `cnt[q] >= full - 1` + 缺口在报告中如实标注

已知数据源缺口：基建投资累计同比（INV_INV_INFRA_CUM_YOY）2026 年 4–7 月连续缺值；出口总额同比、70 城房价、土地出让、LPR/MLF、美国 CPI 无覆盖。

### 5. 定时自动化

任务定义存于工作空间 `.workbuddy/automations/monthly-macro-report.json`（rrule `FREQ=MONTHLY;BYMONTHDAY=10` + run_time 15:00）。若原生 `automation_update` 工具不可用（本环境曾验证不可用），走 WorkBuddy UI 手动创建，prompt 直接引用 JSON 内字段。

---

## 硬性规则

1. **宏观数据必须来自真实接口**，任何缺失值标注为 `—`，禁止插值、编造或"近似"。
2. 时间线独立构建，**不与任何源文件数据对比**（用户明确要求）。
3. 更新前先跑 `update_report.sh` 端到端验证（约 45 秒），再交付。
