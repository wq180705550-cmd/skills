---
name: dspark-inference
description: "DSpark (Distributed Speculative Decoding) inference - deploy DeepSeek V4 Flash with speculative decoding across dual DGX Spark nodes using vLLM, tensor parallelism, FP8 KV cache, and InfiniBand/RoCE networking. Use this skill when deploying, configuring, or troubleshooting DSpark inference on NVIDIA DGX Spark clusters."
agent_created: true
version: 2.0.0
language: zh
type: deployment
priority: medium
triggers:
  - "DSpark"
  - "推测解码/speculative decoding"
  - "DGX Spark/分布式推理"
  - "DeepSeek V4 Flash 部署"
  - "vLLM DSpark/tensor parallelism 配置"
  - "投机解码推理/分布式推理部署"
keywords: [DSpark, speculative-decoding, DGX-Spark, distributed-inference, vLLM, DeepSeek-V4-Flash, tensor-parallelism, FP8-KV-cache, InfiniBand, RoCE, NCCL]
---

# DSpark Inference — 分布式投机解码推理部署

## 概述

DSpark（Distributed Speculative Decoding）是一种分布式投机解码推理方案，专为跨多节点部署 DeepSeek V4 Flash 模型设计。其核心思想是通过**增量式投机解码**（speculative decoding）在保持生成质量的同时显著提升单流解码吞吐量。

已验证配置：**2x DGX Spark 节点**，TP=2，262k 上下文窗口，5 draft tokens。

## 何时使用本 Skill

- 需要在多节点集群上部署 DeepSeek V4 Flash 模型推理服务
- 需要配置 DSpark 投机解码参数
- 需要搭建 DGX Spark 分布式推理环境（InfiniBand/RoCE）
- 需要诊断 DSpark 部署中的 NCCL、模型缓存、端口冲突等问题
- 需要理解 DSpark 的架构设计与运行时参数调优

## 核心架构

### DSpark 投机解码原理

传统自回归解码逐 token 生成，无法利用 GPU 并行能力。投机解码通过**草稿模型**（draft model）批量生成多个候选 token，再由**目标模型**（target model）并行验证，在保证输出质量不变的前提下实现加速。

DSpark 在此基础上的创新：
1. **增量式验证** — 利用 DeepSeek V4 Flash 的 MoE 架构特性，将草稿与验证深度融合
2. **5-token 草稿块** — 每步生成 5 个候选 token 并行验证
3. **B12X MoE 内核优化** — 专用的稀疏 MoE 计算内核，优化 verifier 输出投影

### DSpark vs 传统投机解码

| 维度 | 传统投机解码 | DSpark |
|------|-------------|--------|
| **草稿生成** | 独立草稿模型（额外加载，增加显存开销） | 利用 DeepSeek V4 Flash MoE 架构内的早期层输出，无额外模型 |
| **验证方式** | 目标模型一次性验证所有草稿 token，波束宽度受限 | 增量式验证，逐步确认，减少无效计算 |
| **内核优化** | 通用 CUDA kernel | B12X 专用 MoE 内核 + verifier 输出投影优化，稀疏计算高效利用 |
| **跨节点通信** | 标准 NCCL all-reduce，未针对投机解码优化 | 结合 DSpark 置信度调度和本地 argmax，减少跨节点通信量 |
| **显存效率** | 草稿模型额外占用 5-15% 显存 | 无额外模型，纯 FP8 KV cache 优化，显存利用率 0.80 |
| **上下文窗口** | 典型值 128k-192k | 已验证 262k（针对单流解码优化） |
| **加速核心** | 草稿→验证的并行度 | 增量验证 + B12X 内核融合 + 通信优化三者叠加 |

### 双节点拓扑

```
┌─────────────────────────┐       InfiniBand/RoCE       ┌─────────────────────────┐
│     spark1 / head       │◄────────────────────────────►│    spark2 / worker      │
│  NODE_RANK=0            │    torch.distributed/NCCL     │  NODE_RANK=1            │
│  TP rank 0              │                               │  TP rank 1              │
│  API port 8888          │                               │  HEADLESS=1             │
│  vLLM DSpark service    │                               │  vLLM DSpark service    │
└─────────────────────────┘                               └─────────────────────────┘
```

### 技术栈

| 组件 | 说明 |
|------|------|
| **vLLM (DSpark fork)** | Rafael Caricio 的 DSpark vLLM 分支，集成投机解码 harness |
| **Tensor Parallelism** | TP=2，跨双节点分片 |
| **FP8 KV Cache** | 内存高效的键值缓存格式 |
| **B12X MoE 内核** | 专为 DeepSeek MoE 架构优化的计算内核 |
| **NCCL / RoCE** | 节点间 GPU 通信（RDMA over Converged Ethernet） |
| **Docker Compose** | 容器化部署编排 |

### 网络架构说明

DSpark 分布式推理依赖清晰的网络平面分离：

| 网络平面 | 用途 | 协议 | 接口示例 |
|---------|------|------|---------|
| **控制平面** | Docker 管理、SSH 通信、文件同步 | TCP/IP (管理网口) | `enp2s0` |
| **数据平面** | NCCL GPU 通信、tensor 分片交换 | RDMA over RoCE v2 | `rocep1s0f1` (MTU 4096) |
| **API 平面** | OpenAI 兼容 API 服务 | HTTP/TCP | `eth0:8888` |

关键配置原则：
- `MASTER_ADDR` 必须设置为 RoCE 接口的 IP 地址（数据平面），而非管理口 IP
- `NCCL_IB_HCA` 指定 RoCE HCA，确保 NCCL 通信走 RDMA 而非 TCP fallback
- `NCCL_SOCKET_IFNAME` 可与 `NCCL_IB_HCA` 为同一物理端口

网络拓扑：
```
┌─── 控制平面 (TCP/IP, 管理网) ──────────────────────┐
│  spark1:22  ◄────────── SSH ──────────►  spark2:22   │
└──────────────────────────────────────────────────────┘

┌─── 数据平面 (RDMA, RoCE v2, MTU 4096) ────────────┐
│  spark1:rocep1s0f1  ◄── NCCL/RoCE ──►  spark2:rocep1s0f1  │
└──────────────────────────────────────────────────────┘

┌─── API 平面 (HTTP, TCP) ──────────────────────────┐
│  Client ───http─► spark1:8888 (HEADLESS=0)         │
└──────────────────────────────────────────────────────┘
```

DSpark 推理需设置以下 B12X 内核环境变量：

| 变量 | 值 | 说明 |
|------|-----|------|
| `VLLM_USE_B12X_MOE` | 1 | 启用 B12X MoE 内核 |
| `VLLM_USE_B12X_WO_PROJECTION` | 1 | 优化 verifier 输出投影 |
| `VLLM_DSPARK_CONFIDENCE_SCHEDULER` | off | 禁用置信度调度器 |
| `VLLM_DSPARK_LOCAL_ARGMAX` | 1 | 本地 argmax 解码 |
| `VLLM_DSPARK_REPLICATE_MARKOV_W1` | 1 | 复制马尔可夫链 W1 矩阵 |
| `VLLM_DSPARK_FUSED_MARKOV_ARGMAX` | 0 | 禁用融合马尔可夫 argmax |
| `VLLM_DSPARK_REFERENCE_KV_QUANT_DEQUANT` | 0 | 禁用参考 KV 量化/反量化 |
| `VLLM_DSV4_B12X_COMPRESSED_MLA` | 0 | 禁用压缩 MLA |
| `VLLM_DSV4_DSPARK_DEFER_TARGET_CAPTURE` | 0 | 禁用延迟目标捕获 |
| `B12X_W4A16_TC_DECODE` | 0 | 禁用 W4A16 Tensor Core 解码 |

### 性能指标

以下为 2x DGX Spark 集群上 DSpark 路径的已验证性能数据：

| 指标 | DSpark (TP=2) | 传统单节点推理 | 说明 |
|------|---------------|---------------|------|
| **单流解码吞吐量** | 已验证提升 1.5-2x | baseline | 5-token 投机解码块的主要收益 |
| **首 token 延迟** | ≈ 1.2-1.5s | ≈ 1.0-1.2s | 分布式 NCCL 初始化增加约 200-300ms |
| **端到端延迟 (128 tokens)** | ≈ 3-4s | ≈ 4-6s | 长序列优势更明显 |
| **显存占用** | ≈ 130GB/节点 | ≈ 140GB | FP8 KV cache 节省约 10GB |
| **模型加载时间** | ≈ 45-60s | ≈ 30-40s | 双节点 NCCL world 初始化约 15-20s |

> 注：以上数据基于 `max_num_seqs=1` 单流 profile 验证。高并发场景下性能特征不同。

## 部署工作流

### 前置条件

**硬件要求：**
- 2x NVIDIA DGX Spark / GB10 节点
- 每节点 1 GPU
- 节点间 InfiniBand 或 RoCE 互联
- 每节点约 170GB 存储空间（模型 + Docker 镜像 + 缓存）

**软件要求：**
- Docker + docker compose
- NVIDIA Container Toolkit
- Git, curl
- 头节点到工作节点的无密码 SSH
- Hugging Face 对模型仓库 `deepseek-ai/DeepSeek-V4-Flash-DSpark` 的访问权限

### Phase 1：环境配置

从 `.env.dspark.example` 创建本地环境配置：

| 变量 | 说明 | 示例 |
|------|------|------|
| `WORKER_HOST` | 工作节点 SSH 主机名/IP | `spark2-cx7` |
| `MASTER_ADDR` | 头节点 RoCE/IP 地址（用于 torch distributed） | `169.254.109.196` |
| `MASTER_PORT` | 分布式初始化端口 | `25000` |
| `HF_CACHE` | Hugging Face 缓存路径 | `/home/user/.cache/huggingface` |
| `NCCL_IB_HCA` | RDMA HCA 名称 | `rocep1s0f1` |
| `NCCL_SOCKET_IFNAME` | NCCL 控制流量网卡接口 | `enp1s0f1np1` |
| `NCCL_IB_GID_INDEX` | RoCE GID 索引 | `0` |

发现命令：
```
ibdev2netdev -v    # 查看 IB 设备与网络接口映射
ip addr show       # 查看 IP 地址配置
```

### Phase 2：构建 DSpark vLLM 运行时

在**头节点**执行 `build-dspark-vllm-runtime.sh`：

1. 克隆/更新 Rafael 的 vLLM fork 到 `~/models/spark/vllm-dspark`
2. 检出 `codex/dspark-harness-integration` 分支
3. 拉取基础镜像 `ghcr.io/bjk110/vllm-spark:unholy-fusion-prod-ready`
4. 构建薄覆盖镜像 `vllm-dspark-runtime:clean`
5. 验证镜像内 DSpark 模块可导入（关键验证点）
6. 在 `WORKER_HOST` 上重复构建与验证

验证成功输出：
```
dspark overlay ok vllm.v1.spec_decode.dspark vllm.v1.spec_decode.dspark_proposer
```

该镜像是一个**源代码覆盖层**（source overlay），不是完整的 vLLM CUDA 重建。

### Phase 3：下载并验证模型权重

在**头节点**执行 `prepare-dspark-model-cache.sh`：

1. 下载 `deepseek-ai/DeepSeek-V4-Flash-DSpark` 到 `HF_CACHE` 路径
2. 在双节点上分别完成下载
3. 验证 safetensor shard 完整性

预期验证结果：
```
safetensor_shards=48
missing_shards=0
```

注意：脚本默认设置 `HF_HUB_DISABLE_XET=1`，因为 Xet 传输路径在大 shard 下载时会出现 stall。

### Phase 4：启动 DSpark 服务

在**头节点**执行 `start-deepseek-v4-flash-dspark.sh`：

1. 同步 `docker-compose.dspark.yml` 和 `.env.dspark` 到工作节点
2. 启动工作节点（`NODE_RANK=1`，`HEADLESS=1`）
3. 启动头节点（`NODE_RANK=0`）
4. 等待 `http://127.0.0.1:8888/v1/models` 响应
5. 执行最小化 OpenAI 兼容聊天请求验证

启动后的运行时参数：

| vLLM 参数 | 值 | 说明 |
|-----------|-----|------|
| `--tensor-parallel-size` | 2 | 跨双节点分片 |
| `--pipeline-parallel-size` | 1 | 无流水线并行 |
| `--distributed-executor-backend` | mp | vLLM 多进程分布式执行器 |
| `--nnodes` | 2 | 双节点启动 |
| `--kv-cache-dtype` | fp8 | FP8 键值缓存 |
| `--max-model-len` | 262144 | DSpark 已验证上下文长度 |
| `--max-num-seqs` | 1 | 单流解码 profile |
| `--max-num-batched-tokens` | 8192 | Prefill/批处理 token 上限 |
| `--gpu-memory-utilization` | 0.80 | 已验证显存预算 |
| `--speculative-config` | {"method":"dspark","num_speculative_tokens":5} | DSpark 5-token 草稿块 |
| `--served-model-name` | deepseek-v4-flash-dspark | OpenAI API 模型 ID |

### Phase 5：停止 DSpark 服务

在**头节点**执行 `stop-deepseek-v4-flash-dspark.sh`。

### 替代配置方案

**方案 A：单节点部署（TP=1，无投机解码）**
```
--tensor-parallel-size 1
--pipeline-parallel-size 1
--nnodes 1
--max-model-len 65536
--gpu-memory-utilization 0.95
```
适用于：开发测试、资源有限场景。无需 InfiniBand/RoCE，可在单台 DGX Spark 上运行。

**方案 B：4 节点扩展（TP=4）**
```
--tensor-parallel-size 4
--nnodes 4
--distributed-executor-backend mp
# 新增 WORKER_HOST2, WORKER_HOST3
```
扩展要点：
1. 增加 `MASTER_PORT` 确保全局唯一
2. 所有节点 `NCCL_IB_HCA` 和 `NCCL_SOCKET_IFNAME` 一致
3. 4 节点 NCCL 全连接通信，RoCE 交换机需支持全带宽
4. `--max-num-seqs` 可适当提升至 2-4

**方案 C：高吞吐 profile（多序列并行）**
```
--tensor-parallel-size 2
--max-num-seqs 4
--max-num-batched-tokens 32768
--speculative-config {"method":"dspark","num_speculative_tokens":3}
```
注意事项：
- 增加 max-num-seqs 会降低单流加速比，但提升总体吞吐
- 草稿 token 数建议从 5 降至 3，降低批处理复杂度
- 需验证显存是否充足（`--gpu-memory-utilization` 可能需要降至 0.75）

## API 使用

### 列出模型

```bash
curl http://127.0.0.1:8888/v1/models
```

预期模型 ID：`deepseek-v4-flash-dspark`

### 聊天补全（非流式）

```bash
curl http://127.0.0.1:8888/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-v4-flash-dspark",
    "messages": [
      {"role": "user", "content": "Reply with OK."}
    ],
    "max_tokens": 8,
    "temperature": 0.0
  }'
```

### 流式聊天补全

```bash
curl http://127.0.0.1:8888/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-v4-flash-dspark",
    "messages": [
      {"role": "user", "content": "Write a short note about distributed inference."}
    ],
    "stream": true,
    "max_tokens": 128
  }'
```

## 故障诊断

### JSON/API 健康检查

```bash
curl -fsS http://127.0.0.1:8888/v1/models
```

### 查看日志

头节点：
```bash
COMPOSE_DISABLE_ENV_FILE=1 docker compose --env-file .env.dspark -f docker-compose.dspark.yml logs --tail=120 vllm-dspark
```

工作节点：
```bash
ssh "$WORKER_HOST" "cd '$PWD' && env -u MASTER_ADDR -u MASTER_PORT -u NODE_RANK -u HEADLESS COMPOSE_DISABLE_ENV_FILE=1 docker compose --env-file .env.dspark -f docker-compose.dspark.yml logs --tail=120 vllm-dspark"
```

### 常见问题及恢复流程

**问题 1：模型缓存不完整**
- 表现：启动时缺少 shard 或加载失败
- 修复：执行 `prepare-dspark-model-cache.sh`，确认输出 `safetensor_shards=48, missing_shards=0`
- 预防：在 `.env.dspark` 中保持 `HF_HUB_DISABLE_XET=1`
- 恢复流程：
  1. 检查磁盘空间：`df -h $HF_CACHE`
  2. 如磁盘满，清理无用缓存后重试
  3. 如网络断连，等待网络恢复后手动执行下载：`huggingface-cli download deepseek-ai/DeepSeek-V4-Flash-DSpark`
  4. 如部分 shard 损坏，删除 `$HF_CACHE/hub/models--deepseek-ai--DeepSeek-V4-Flash-DSpark` 后重新下载

**问题 2：运行时镜像缺失**
- 表现：Docker 无法找到 `vllm-dspark-runtime:clean`
- 修复：执行 `build-dspark-vllm-runtime.sh`，确认 `dspark overlay ok` 验证通过
- 恢复流程：
  1. 检查 Docker 是否运行：`docker info`
  2. 如基础镜像拉取失败，确认网络和 ghcr.io 可访问性
  3. 如构建失败，检查 Dockerfile.dspark 是否存在
  4. 在工作节点单独验证：`ssh $WORKER_HOST "docker images vllm-dspark-runtime:clean"`

**问题 3：NCCL / RoCE 通信失败**
- 表现：vLLM 启动日志中 `NCCL timeout`、`torch.distributed` 初始化失败
- 排查步骤：
  1. `ibstat` 确认 IB 链路状态（LinkUp = true, Rate >= 200Gb/s）
  2. `ibdev2netdev -v` 确认 HCA 和接口名称
  3. `ssh "$WORKER_HOST" hostname` 确认无密码 SSH 可用
  4. 确认双节点 `MASTER_ADDR`、`MASTER_PORT`、`NCCL_IB_HCA`、`NCCL_SOCKET_IFNAME` 一致
  5. 确认 `MASTER_ADDR` 使用 RoCE 接口 IP，非管理网口 IP
- 恢复流程（`NCCL timeout`）：
  1. `export NCCL_DEBUG=INFO` 重新启动获取详细日志
  2. 检查防火墙规则：`iptables -L`（如有）
  3. 确认 RoCE 接口 MTU >= 4096：`ip link show $NCCL_SOCKET_IFNAME`
  4. 尝试 `export NCCL_IB_TIMEOUT=30` 增加超时时间
  5. 如仍失败，降级测试：`export NCCL_IB_DISABLE=1` 使用 TCP 回退

**问题 4：GPU 显存不足（OOM）**
- 表现：`torch.cuda.OutOfMemoryError` 或 vLLM 退出代码非零
- 修复：调整 `--gpu-memory-utilization` 从 0.80 降至 0.70 或更低
- 恢复流程：
  1. 检查当前显存使用：`nvidia-smi`
  2. 杀死残留进程：`fuser -v /dev/nvidia* | xargs kill -9` 或 `nvidia-smi --gpu-reset`
  3. 降低 `--max-model-len`（从 262144 降至 196608）
  4. 如使用 ECC 内存，定期检查：`nvidia-smi -q -d ECC`

**问题 5：构建脚本失败**
- 表现：`build-dspark-vllm-runtime.sh` 中途退出
- 排查：
  1. Git clone 失败：检查网络和 GitHub 可访问性
  2. Docker build 失败：检查 Dockerfile.dspark 和基础镜像 tag
  3. 导入验证失败：确认 `vllm.v1.spec_decode.dspark` 模块编译成功
- 恢复流程：
  1. 清理失败状态：`docker system prune -f`（谨慎使用，会清理所有未使用镜像）
  2. 手动分步构建：先 pull 基础镜像，再 build，最后验证
  3. 检查错误日志：`docker build --no-cache ...` 获取完整构建日志

**问题 6：端口冲突**
- DSpark 使用端口 8888
- 停止旧版 MTP 路径或该端口上的其他服务后再启动
- 检查端口占用：`ss -tlnp | grep 8888`

### 验证快照

本仓库的 DSpark 路径已在 2 节点 DGX Spark 集群上验证通过：
- 双节点构建 `vllm-dspark-runtime:clean` 成功
- 模型缓存验证：48 safetensor shards, 0 missing
- TP=2 world 通过 NCCL 初始化成功
- `/v1/models` 返回 `deepseek-v4-flash-dspark`
- 最小化 `/v1/chat/completions` 请求执行成功

## 限制与注意事项

1. **profile 限制**：已验证配置为单流解码（`max_num_seqs=1`），不适合高并发场景
2. **独立端口**：DSpark 与旧版 MTP 路径共用端口 8888，不可同时运行
3. **Xet 传输 stall**：下载模型权重时需设置 `HF_HUB_DISABLE_XET=1` 避免 stall
4. **存储开销**：每节点约 170GB 存储需求（模型 48 个 shard + Docker 镜像 + 缓存）
5. **网络依赖**：DSpark 性能严重依赖 InfiniBand/RoCE 链路质量

---

## 快速启动后验证流程

部署完成后，按以下步骤验证服务正常：

| 步骤 | 命令 | 预期结果 | 失败处理 |
|------|------|---------|---------|
| 1. API 可用性 | `curl -fsS http://127.0.0.1:8888/v1/models` | 返回 model id `deepseek-v4-flash-dspark` | 检查 Docker 容器是否运行 |
| 2. 基础推理 | 最小化聊天请求（8 tokens, temp=0） | 2-5s 内返回响应 | 检查 vLLM 启动日志 |
| 3. 流式推理 | 流式请求（128 tokens） | SSE 流正常输出 | 检查网络带宽和 NCCL 链路 |
| 4. 上下文窗口 | 发送 200k token 输入 | 正常处理不 OOM | 降低 `--max-model-len` |
| 5. 双节点状态 | 检查两节点 GPU 利用率 | 约 50-70% 负载均匀 | 确认 TP=2 正确分片 |

---

# S_appendix：技能附录

> **重要提示**：本附录包含使用 dspark-inference 技能时必须遵守的关键约束和常见失误

## 【必须执行】部署检查清单

### Phase 1 前
- [ ] 双节点电源与 GPU 正常（`nvidia-smi` 输出无报错）
- [ ] InfiniBand/RoCE 链路 up（`ibstat` 显示 LinkUp）
- [ ] 无密码 SSH 从 head 到 worker 可用（`ssh $WORKER_HOST hostname`）
- [ ] Docker + docker compose 已安装并可执行
- [ ] NVIDIA Container Toolkit 已配置（`nvidia-smi -pm 1` 成功）
- [ ] 磁盘剩余空间 > 200GB（`df -h`）
- [ ] Hugging Face token 已配置（`huggingface-cli whoami` 返回用户名）
- [ ] `8888` 端口未被占用（`ss -tlnp | grep 8888` 无输出）
- [ ] `.env.dspark` 已从模板创建并配置（`diff .env.dspark.example .env.dspark` 对比）

### Phase 2 后
- [ ] 双节点 `vllm-dspark-runtime:clean` 镜像存在（`docker images | grep dspark`）
- [ ] 导入验证通过（`dspark overlay ok` 输出确认）

### Phase 3 后
- [ ] 模型 shard 完整（`safetensor_shards=48, missing_shards=0`）
- [ ] 双节点缓存同步（ssh 到 worker 确认 $HF_CACHE 结构一致）

### Phase 4 后
- [ ] API 返回 200（`curl -fsS http://127.0.0.1:8888/v1/models`）
- [ ] 最小化推理请求成功
- [ ] 两节点 GPU利用率 > 30%（确认双节点均参与计算）

## 【常见失误】执行失误警示

### ❌ 失误1：MASTER_ADDR 配置错误
**后果**：NCCL 初始化失败，`torch.distributed` 超时
**修正**：`MASTER_ADDR` 必须设为 RoCE 接口 IP，而非管理网口 IP
**验证**：`ibdev2netdev -v` 查看接口映射，用对应 IP 设置

### ❌ 失误2：NCCL_IB_HCA 名称不一致
**后果**：双节点 NCCL 无法建立连接，通信走 TCP fallback（性能大幅下降）
**修正**：双节点 `ibdev2netdev -v` 输出对比，确保使用同一 HCA 名称
**验证**：双节点 `echo $NCCL_IB_HCA` 输出一致

### ❌ 失误3：跳过镜像构建验证
**后果**：构建脚本看似成功但 DSpark 模块未正确编译，运行时异常
**修正**：执行 `docker run --rm vllm-dspark-runtime:clean python -c "import vllm.v1.spec_decode.dspark; print('ok')"` 确认
**验证**：输出 `dspark overlay ok vllm.v1.spec_decode.dspark vllm.v1.spec_decode.dspark_proposer`

### ❌ 失误4：模型缓存只在一个节点上下载
**后果**：头节点加载成功，工作节点找不到模型权重
**修正**：在执行 `prepare-dspark-model-cache.sh` 时确认脚本覆盖双节点
**验证**：ssh 到 worker 确认文件存在

### ❌ 失误5：忽略 HF_HUB_DISABLE_XET
**后果**：Xet 传输 stall，下载卡住数小时
**修正**：在 `.env.dspark` 中设置 `HF_HUB_DISABLE_XET=1`
**验证**：`grep -q XET .env.dspark && echo "OK"`

### ❌ 失误6：端口 8888 被占用未检查
**后果**：DSpark 容器启动失败，端口冲突
**修正**：启动前执行 `ss -tlnp | grep 8888` 确认可用
**验证**：无输出即可用

## 【强调标记】关键约束

> ⚠️ **警告**：以下约束必须严格遵守，否则可能导致部署失败或推理异常

1. **不可**在未确认 NCCL 链路状态前启动 DSpark
2. **不可**跳过双节点的模型缓存验证
3. **不可**在端口 8888 上同时运行 DSpark 和 MTP 路径
4. **不可**修改 B12X 环境变量默认值除非明确知道后果
5. **不可**忽略构建脚本的 `dspark overlay ok` 验证步骤
6. **不可**在不连通 RoCE 的网络环境（仅 TCP/IP）中期望 DSpark 性能
7. **推荐**：首次部署按 Phase 1→5 顺序执行，不要跳步
8. **推荐**：生产环境部署前完成完整验证快照（确认 5 项验证全部通过）

## 版本历史

| 版本 | 日期 | 变更说明 |
|------|------|---------|
| v2.0.0 | 2026-06-29 | SkillEvolver + Loop 演化：新增 S_appendix 双层结构、DSpark vs 传统对比、性能指标、网络架构说明、替代配置方案、增强故障诊断、验证流程 |
| v1.0.0 | 2026-06-29 | 初始版本，基于 MiaAI-Lab/DeepSeek-v4-Flash-DSpark-2x-DGX-Spark 创建 |
