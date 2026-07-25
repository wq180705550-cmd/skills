# DSpark 部署脚本参考

## 启动流程详解

### start-deepseek-v4-flash-dspark.sh 执行流程

1. **同步配置文件到工作节点**
   ```bash
   rsync -avz docker-compose.dspark.yml $WORKER_HOST:$PWD/
   rsync -avz .env.dspark $WORKER_HOST:$PWD/
   ```

2. **启动工作节点（HEADLESS 模式）**
   ```bash
   ssh $WORKER_HOST "cd $PWD && \
     NODE_RANK=1 HEADLESS=1 \
     docker compose --env-file .env.dspark -f docker-compose.dspark.yml up -d vllm-dspark"
   ```
   - `NODE_RANK=1`: 标识为第二个节点
   - `HEADLESS=1`: 不启动 API 服务，仅作为 TP rank 1 参与计算
   - `-d`: 后台运行

3. **启动头节点（API 模式）**
   ```bash
   NODE_RANK=0 HEADLESS=0 \
     docker compose --env-file .env.dspark -f docker-compose.dspark.yml up -d vllm-dspark
   ```
   - `NODE_RANK=0`: 标识为主节点
   - `HEADLESS=0`: 启动 API 服务（端口 8888）

4. **等待服务就绪**
   ```bash
   for i in $(seq 1 30); do
     if curl -fsS http://127.0.0.1:8888/v1/models > /dev/null 2>&1; then
       echo "DSpark server is ready."
       break
     fi
     sleep 10
   done
   ```

5. **运行验证请求**
   ```bash
   curl http://127.0.0.1:8888/v1/chat/completions \
     -H "Content-Type: application/json" \
     -d '{
       "model": "deepseek-v4-flash-dspark",
       "messages": [{"role": "user", "content": "Reply with OK."}],
       "max_tokens": 8,
       "temperature": 0.0
     }'
   ```

### stop-deepseek-v4-flash-dspark.sh 执行流程

1. **停止头节点服务**
   ```bash
   docker compose --env-file .env.dspark -f docker-compose.dspark.yml down vllm-dspark
   ```

2. **停止工作节点服务**
   ```bash
   ssh $WORKER_HOST "cd $PWD && \
     docker compose --env-file .env.dspark -f docker-compose.dspark.yml down vllm-dspark"
   ```

### build-dspark-vllm-runtime.sh 执行流程

1. **克隆/更新 vLLM DSpark fork**
   ```bash
   VLLM_DIR=~/models/spark/vllm-dspark
   if [ -d "$VLLM_DIR" ]; then
     cd "$VLLM_DIR" && git pull
   else
     mkdir -p ~/models/spark
     git clone https://github.com/rafaelcaricio/vllm.git "$VLLM_DIR"
   fi
   git checkout codex/dspark-harness-integration
   ```

2. **拉取基础镜像**
   ```bash
   docker pull ghcr.io/bjk110/vllm-spark:unholy-fusion-prod-ready
   ```

3. **构建覆盖镜像**
   ```bash
   docker build -t vllm-dspark-runtime:clean \
     --build-arg BASE_IMAGE=ghcr.io/bjk110/vllm-spark:unholy-fusion-prod-ready \
     -f Dockerfile.dspark .
   ```

4. **验证镜像内 DSpark 模块**
   ```bash
   docker run --rm vllm-dspark-runtime:clean \
     python -c "import vllm.v1.spec_decode.dspark; import vllm.v1.spec_decode.dspark_proposer; print('dspark overlay ok')"
   ```

5. **在工作节点上重复 1-4**
   ```bash
   ssh $WORKER_HOST "$(curl -fsSL \#...)"  # 通过 SSH 执行相同脚本
   ```

### prepare-dspark-model-cache.sh 执行流程

1. **安装 huggingface-cli**（如未安装）
   ```bash
   pip install -U "huggingface_hub[cli]"
   ```

2. **登录 Hugging Face**（如需）
   ```bash
   huggingface-cli login --token $HF_TOKEN
   ```

3. **下载模型权重到缓存路径**
   ```bash
   huggingface-cli download deepseek-ai/DeepSeek-V4-Flash-DSpark \
     --local-dir $HF_CACHE/hub/models--deepseek-ai--DeepSeek-V4-Flash-DSpark
   ```

4. **验证 shard 完整性**
   ```bash
   SHARD_COUNT=$(find $HF_CACHE/hub/models--deepseek-ai--DeepSeek-V4-Flash-DSpark \
     -name "*.safetensors" | wc -l)
   echo "safetensor_shards=$SHARD_COUNT"
   
   MISSING_COUNT=$(ls $HF_CACHE/hub/models--deepseek-ai--DeepSeek-V4-Flash-DSpark/ \
     2>/dev/null | grep -c "incomplete\|stale" || echo 0)
   echo "missing_shards=$MISSING_COUNT"
   ```

5. **在工作节点上重复 3-4**
   ```bash
   ssh $WORKER_HOST "cd $PWD && bash prepare-dspark-model-cache.sh --worker-only"
   ```

## 快速启动检查清单

### 部署前检查

- [ ] 双节点电源正常，GPU 可用（`nvidia-smi`）
- [ ] InfiniBand/RoCE 链路 up（`ibstat`）
- [ ] 无密码 SSH 从 head 到 worker 可用（`ssh $WORKER_HOST hostname`）
- [ ] Docker 和 docker compose 已安装
- [ ] NVIDIA Container Toolkit已配置
- [ ] 磁盘剩余空间 > 200GB
- [ ] Hugging Face 访问令牌已配置
- [ ] 端口 8888 未被占用
- [ ] `.env.dspark` 已从模板创建并配置正确
- [ ] `MASTER_ADDR` 使用 RoCE/IP 地址（非管理口 IP）
- [ ] 双节点 `NCCL_IB_HCA` 和 `NCCL_SOCKET_IFNAME` 一致

### 部署顺序

1. [ ] `cp .env.dspark.example .env.dspark` → 编辑配置
2. [ ] `./build-dspark-vllm-runtime.sh` → 双节点构建（约 10-15 分钟）
3. [ ] `./prepare-dspark-model-cache.sh` → 双节点下载（约 30-60 分钟，视带宽而定）
4. [ ] 确认模型缓存完整：48 shards, 0 missing
5. [ ] `./start-deepseek-v4-flash-dspark.sh` → 启动服务
6. [ ] `curl http://127.0.0.1:8888/v1/models` → 确认 API 就绪
7. [ ] 执行聊天补全请求验证推理可用
