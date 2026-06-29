---
name: dspark-inference
description: "DSpark (Distributed Speculative Decoding) inference - deploy DeepSeek V4 Flash with speculative decoding across dual DGX Spark nodes using vLLM, tensor parallelism, FP8 KV cache, and InfiniBand/RoCE networking. Use this skill when deploying, configuring, or troubleshooting DSpark inference on NVIDIA DGX Spark clusters."
agent_created: true
version: 1.0.0
language: zh
type: deployment
priority: medium
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

### B12X 环境变量

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

### 常见问题

**问题 1：模型缓存不完整**
- 表现：启动时缺少 shard 或加载失败
- 修复：执行 `prepare-dspark-model-cache.sh`，确认输出 `safetensor_shards=48, missing_shards=0`
- 预防：在 `.env.dspark` 中保持 `HF_HUB_DISABLE_XET=1`

**问题 2：运行时镜像缺失**
- 表现：Docker 无法找到 `vllm-dspark-runtime:clean`
- 修复：执行 `build-dspark-vllm-runtime.sh`，确认 `dspark overlay ok` 验证通过

**问题 3：NCCL / RoCE 通信失败**
- 排查步骤：
  1. `ibstat` 确认 IB 链路状态
  2. `ibdev2netdev -v` 确认 HCA 和接口名称
  3. `ssh "$WORKER_HOST" hostname` 确认无密码 SSH 可用
  4. 确认双节点 `MASTER_ADDR`、`MASTER_PORT`、`NCCL_IB_HCA`、`NCCL_SOCKET_IFNAME` 一致

**问题 4：端口冲突**
- DSpark 使用端口 8888
- 停止旧版 MTP 路径或该端口上的其他服务后再启动

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

## 相关资源

- Hugging Face 模型：`deepseek-ai/DeepSeek-V4-Flash-DSpark`
- vLLM DSpark PR：`rafaelcaricio/vllm#1`
- Docker 部署 PR：`rafaelcaricio/spark_vllm_docker#1`
- 参考仓库：`MiaAI-Lab/DeepSeek-v4-Flash-DSpark-2x-DGX-Spark`

详细的环境配置模板和 Docker Compose 文件见 references/ 目录。
