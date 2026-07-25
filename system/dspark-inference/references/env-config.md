# DSpark 环境配置参考

## 环境变量模板（.env.dspark）

```bash
# === DSpark Inference Environment Configuration ===

# --- Cluster Topology ---
WORKER_HOST=spark2-cx7
# SSH hostname or IP for the worker node

MASTER_ADDR=169.254.109.196
# Head-node RoCE/IP address used by torch distributed
# This is the IP that NCCL workers use to reach rank 0

MASTER_PORT=25000
# Distributed init port (must match on both nodes)

NODE_RANK=0
# Set to 0 on head node, 1 on worker node
# Controlled by start script, not in env file directly

HEADLESS=0
# Set to 1 on worker node (no API server)
# Controlled by start script, not in env file directly

# --- Model Cache ---
HF_CACHE=/home/user/.cache/huggingface
# Host Hugging Face cache path
# Model weights are downloaded here: $HF_CACHE/hub/
# Requirements: ~170GB free space

HF_HUB_DISABLE_XET=1
# Disable Xet transfer to avoid stalls during large shard downloads

# --- NCCL / RDMA ---
NCCL_IB_HCA=rocep1s0f1
# RDMA HCA name — use `ibdev2netdev -v` to discover

NCCL_SOCKET_IFNAME=enp1s0f1np1
# Socket interface for NCCL control traffic

NCCL_IB_GID_INDEX=0
# RoCE GID index — usually 0 or 3

# --- DSpark / B12X Kernel Flags ---
VLLM_USE_B12X_MOE=1
VLLM_USE_B12X_WO_PROJECTION=1
VLLM_DSPARK_CONFIDENCE_SCHEDULER=off
VLLM_DSPARK_LOCAL_ARGMAX=1
VLLM_DSPARK_REPLICATE_MARKOV_W1=1
VLLM_DSPARK_FUSED_MARKOV_ARGMAX=0
VLLM_DSPARK_REFERENCE_KV_QUANT_DEQUANT=0
VLLM_DSV4_B12X_COMPRESSED_MLA=0
VLLM_DSV4_DSPARK_DEFER_TARGET_CAPTURE=0
B12X_W4A16_TC_DECODE=0
```

## 网络接口发现命令

```bash
# 查看 InfiniBand 设备与网络接口映射
ibdev2netdev -v

# 输出示例：
# mlx5_0 (MT4129 - ConnectX-7) fw 40.38.1000 port 1 (link up) :: rocep1s0f1

# 查看 IP 地址配置
ip addr show

# 查看 IB 链路状态
ibstat

# 查看 RoCE GID 索引
show_gids
```

## vLLM DSpark 运行时参数详解

### 核心参数

| 参数 | 值范围 | 说明 |
|------|--------|------|
| `--tensor-parallel-size` | 1-8 | 张量并行度，等于 GPU 总数。DSpark 已验证 TP=2 |
| `--pipeline-parallel-size` | 1 | 流水线并行度。DSpark 不启用流水线并行 |
| `--distributed-executor-backend` | mp / ray | 分布式执行器后端。DSpark 使用多进程（mp） |
| `--nnodes` | 1-N | 节点总数。DSpark 已验证 2 节点 |
| `--kv-cache-dtype` | fp8 / fp16 / auto | KV 缓存数据类型。DSpark 使用 FP8 |
| `--max-model-len` | 4096-262144 | 最大上下文长度。DSpark 已验证 262144 |
| `--max-num-seqs` | 1-256 | 最大并行序列数。DSpark 单流为 1 |
| `--max-num-batched-tokens` | 2048-65536 | 批处理 token 上限。DSpark 为 8192 |
| `--gpu-memory-utilization` | 0.0-1.0 | GPU 显存利用率预算。DSpark 为 0.80 |

### 投机解码参数

`--speculative-config` 是一个 JSON 对象：

```json
{
  "method": "dspark",
  "num_speculative_tokens": 5
}
```

- `method`: 投机解码方法，必须为 `"dspark"`
- `num_speculative_tokens`: 每步生成的草稿 token 数，DSpark 验证值为 5

### 服务参数

| 参数 | 值 | 说明 |
|------|-----|------|
| `--served-model-name` | deepseek-v4-flash-dspark | OpenAI API 公开的模型名称 |
| `--api-key` | (optional) | API 认证密钥 |
| `--host` | 0.0.0.0 | API 监听地址 |
| `--port` | 8888 | API 监听端口 |

## Docker Compose 服务定义

```yaml
services:
  vllm-dspark:
    image: vllm-dspark-runtime:clean
    container_name: vllm-dspark
    runtime: nvidia
    environment:
      - NODE_RANK=${NODE_RANK}
      - HEADLESS=${HEADLESS:-0}
      - MASTER_ADDR=${MASTER_ADDR}
      - MASTER_PORT=${MASTER_PORT}
      - NCCL_IB_HCA=${NCCL_IB_HCA}
      - NCCL_SOCKET_IFNAME=${NCCL_SOCKET_IFNAME}
      - NCCL_IB_GID_INDEX=${NCCL_IB_GID_INDEX}
      - VLLM_USE_B12X_MOE=${VLLM_USE_B12X_MOE:-1}
      - VLLM_USE_B12X_WO_PROJECTION=${VLLM_USE_B12X_WO_PROJECTION:-1}
      - VLLM_DSPARK_CONFIDENCE_SCHEDULER=${VLLM_DSPARK_CONFIDENCE_SCHEDULER:-off}
      - VLLM_DSPARK_LOCAL_ARGMAX=${VLLM_DSPARK_LOCAL_ARGMAX:-1}
      - VLLM_DSPARK_REPLICATE_MARKOV_W1=${VLLM_DSPARK_REPLICATE_MARKOV_W1:-1}
      - VLLM_DSPARK_FUSED_MARKOV_ARGMAX=${VLLM_DSPARK_FUSED_MARKOV_ARGMAX:-0}
      - VLLM_DSPARK_REFERENCE_KV_QUANT_DEQUANT=${VLLM_DSPARK_REFERENCE_KV_QUANT_DEQUANT:-0}
      - VLLM_DSV4_B12X_COMPRESSED_MLA=${VLLM_DSV4_B12X_COMPRESSED_MLA:-0}
      - VLLM_DSV4_DSPARK_DEFER_TARGET_CAPTURE=${VLLM_DSV4_DSPARK_DEFER_TARGET_CAPTURE:-0}
      - B12X_W4A16_TC_DECODE=${B12X_W4A16_TC_DECODE:-0}
    volumes:
      - ${HF_CACHE}:/root/.cache/huggingface
    ports:
      - "8888:8888"
    command: >
      vllm serve deepseek-ai/DeepSeek-V4-Flash-DSpark
      --tensor-parallel-size 2
      --pipeline-parallel-size 1
      --distributed-executor-backend mp
      --nnodes 2
      --kv-cache-dtype fp8
      --max-model-len 262144
      --max-num-seqs 1
      --max-num-batched-tokens 8192
      --gpu-memory-utilization 0.80
      --speculative-config '{"method":"dspark","num_speculative_tokens":5}'
      --served-model-name deepseek-v4-flash-dspark
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
    networks:
      - dspark-net

networks:
  dspark-net:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

## 模型缓存结构

```
$HF_CACHE/hub/
├── models--deepseek-ai--DeepSeek-V4-Flash-DSpark/
│   ├── blobs/                          # 实际下载的 shard 文件
│   │   ├── model-00001-of-00048.safetensors
│   │   ├── model-00002-of-00048.safetensors
│   │   └── ...
│   ├── refs/                           # 分支/标签引用
│   ├── snapshots/                      # 快照文件
│   └── .locks/                         # 文件锁
```

- 总 shard 数：48 个 safetensor 文件
- 总大小：约 170GB
