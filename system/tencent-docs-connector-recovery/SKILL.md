---
name: tencent-docs-connector-recovery
description: 腾讯文档（tencent-docs 插件）写入报 no_token 时的三段式定位，与「先落盘待写值 → 等连接器恢复 → 幂等补写」的恢复流程。适用于定时自动化向腾讯文档表格写数因宿主连接器掉线而失败的情形。触发词：no_token、腾讯文档写入失败、连接器未连接、not_connected、connector_disabled、票据失效、set_cell_value 失败、写入被阻断、待写值落盘、幂等补跑、补写。
agent_created: true
---

# 腾讯文档 no_token 诊断与恢复

## 症状

腾讯文档插件 `call_tool` 返回 `err=no_token`（或 `ERROR:no_token`），读写全部失败。
`TDoc()` 构造期的插件探测在**任何 HTTP 调用之前**就抛错 ⇒ 文档未被触碰，**无副作用、无需回滚**。

## 三段式定位（由外到内，30 秒出结论）

1. **会话连接器态**：看当前会话 connector-status 是否列出 `tencent-docs ... connected`；不在列表中即可基本判定未连接。
2. **环境变量**：`TDOC_OAUTH_ACCESS_TOKEN` / `TDOC_ONEID_ACCESS_TOKEN` 是否有宿主注入。有则走 env 分支，问题不在此。
3. **网关凭据端点直查**（关键一步，一次拿全 `reason`）：

   ```python
   import os, json, urllib.request
   cfg = json.loads(os.environ["CODEBUDDY_MCP_CONFIG"])
   srv = cfg["mcpServers"]["connector-proxy"]        # 旧名 "workbuddy" 兜底
   req = urllib.request.Request(
       srv["url"] + "/internal/tencent-docs/tokens",
       headers=srv["headers"], method="GET")          # Authorization + X-WorkBuddy-MCP-Context 必须整组透传
   op = urllib.request.build_opener(urllib.request.ProxyHandler({}))   # 走宿主本地，固定不走代理
   print(json.load(op.open(req, timeout=10)))
   ```

   读法：

   | 返回 | 含义 | 处置 |
   |---|---|---|
   | `personal.available=true` | 票据可用 | 问题不在连接器，另查 |
   | `personal.reason=not_connected` | **用户在连接器页未连接/已掉线** | Agent 无法自修，须用户操作 |
   | `enterprise.reason=connector_disabled` | 企业版未启用 | 无害，个人票据可用即可 |
   | `provider HTTP 401` | 网关上下文头被裁 | 检查 headers 是否整组透传 |
   | `no_mcp_config` / `provider unreachable` | 环境/网络问题 | 另查 |

## 关键判据（最易误判处）

- `no_token` 是**会话级、非持久**态：同日可在数十分钟内自行恢复或被用户恢复
  （实测 2026-09-28：12:54 `not_connected` → 13:15 恢复后写入成功）。
- **不要**据「昨天/早上能写」推定「现在也能写」；也**不要**判为数据源或脚本故障 —— `no_token` 与取数链路无关。
- 判定顺序：先看 `reason` 再动作；`not_connected` 是授权态问题，不是网络/代码问题。

## 恢复动作（正确顺序）

1. **先把值算好并落盘**：取数通常不受连接器影响（走 westock CLI 等结构化数据源即可）。
   记录 `待写 {row, col, value}` 与补写命令，并输出给用户。
2. **不要寻找不存在的能力**：无原生腾讯文档 MCP 写工具；写入唯一路径是 `tencent-docs` 插件 + 宿主票据。
3. **等待恢复**：请用户在连接器管理页恢复「腾讯文档」授权（`not_connected` 只能由用户操作）。
4. **恢复后幂等补跑**：本项目成交额脚本为 `python fill_pair.py --at {0945|1030|1430}`。
   此类脚本「识别目标格为空才写 / 值一致则跳过」，**重跑安全**；
   分时柱已冻结时（如 1030 柱），补写值与准点值相同，晚跑不改变结果。
5. **回读校验**：独立脚本读回目标行，确认 `[日期标签, 前值, 本次值]` 且前序行未受影响。

## 反例（不要做）

- 不要把结果改写进 HTML/本地文件或换存处 —— 交付目标就是那张表。
- 不要盲目重复跑写入脚本数十次；先定位 `reason` 再决定。
- 不要触碰宿主数据库、不改网关配置、不臆造连接器凭证。
