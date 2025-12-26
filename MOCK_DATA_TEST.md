# Mock Data 测试指南

## ✅ 已完成的API

所有API已实现**完整的假数据支持**，无需数据库初始化即可测试前端！

### 1. Models API (/api/v1/models)
- ✅ 12个模拟模型 (6个base + 6个adapter)
- ✅ 支持分页、过滤 (status, type, search)
- ✅ 模型详情 (baseline_probe, prompt_contracts, evaluation_summary)
- ✅ Baseline Probe 执行
- ✅ 评估历史查询

### 2. Datasets API (/api/v1/datasets)
- ✅ 20个模拟数据集 (human/synthetic/mixed)
- ✅ 支持分页、过滤 (status, type, scene, direction, search)
- ✅ 数据集详情 (overview, quality_gate, usage_history)
- ✅ Quality Gate 结果
- ✅ 生成估算

### 3. Experiments API (/api/v1/experiments)
- ✅ 15个模拟实验 (pending/running/completed/failed)
- ✅ 支持分页、过滤 (status, model_id, search)
- ✅ 实验详情 (config, progress, logs, metrics)
- ✅ 启动/停止实验
- ✅ 日志查询

### 4. Evaluations API (/api/v1/evaluations)
- ✅ 20个模拟评测 (spoken/written)
- ✅ 支持分页、过滤 (track, experiment_id)
- ✅ 评测详情 (metrics, error_analysis, sample_results)
- ✅ 实验评测摘要 (spoken/written对比)

## 🚀 快速启动测试

### 方法1: 仅启动FastAPI (推荐快速测试)

```bash
cd /home/sharp/AI/VeriAI/Veri-Train

# 使用 uv 安装依赖 (超快!)
uv sync

# 直接启动 (无需数据库!)
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**访问**:
- API文档: http://localhost:8000/api/v1/docs
- 健康检查: http://localhost:8000/health

### 方法2: Docker完整启动 (包含数据库)

```bash
cd /home/sharp/AI/VeriAI/Veri-Train

# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f api
```

**访问**:
- API文档: http://localhost:8000/api/v1/docs
- Flower (Celery监控): http://localhost:5555

## 📋 API测试清单

### 1. Models API

```bash
# 获取模型列表
curl http://localhost:8000/api/v1/models

# 过滤: 只看base模型
curl "http://localhost:8000/api/v1/models?type=base"

# 过滤: 只看available状态
curl "http://localhost:8000/api/v1/models?status=available"

# 搜索模型
curl "http://localhost:8000/api/v1/models?search=gpt"

# 获取模型详情 (先从列表中复制一个ID)
curl http://localhost:8000/api/v1/models/{model_id}

# 执行Baseline Probe
curl -X POST http://localhost:8000/api/v1/models/{model_id}/probe

# 获取评估历史
curl http://localhost:8000/api/v1/models/{model_id}/evaluations
```

### 2. Datasets API

```bash
# 获取数据集列表
curl http://localhost:8000/api/v1/datasets

# 过滤: 只看passed状态
curl "http://localhost:8000/api/v1/datasets?status=passed"

# 过滤: ja-en方向
curl "http://localhost:8000/api/v1/datasets?direction=ja-en"

# 过滤: meeting场景
curl "http://localhost:8000/api/v1/datasets?scene=meeting"

# 获取数据集详情
curl http://localhost:8000/api/v1/datasets/{dataset_id}

# 获取Quality Gate结果
curl http://localhost:8000/api/v1/datasets/{dataset_id}/quality-gate

# 生成估算
curl -X POST http://localhost:8000/api/v1/datasets/generate/estimate \
  -H "Content-Type: application/json" \
  -d '{"target_count": 1000, "language_direction": "ja-en", "scene": "meeting"}'
```

### 3. Experiments API

```bash
# 获取实验列表
curl http://localhost:8000/api/v1/experiments

# 过滤: 只看运行中的
curl "http://localhost:8000/api/v1/experiments?status=running"

# 过滤: 只看已完成的
curl "http://localhost:8000/api/v1/experiments?status=completed"

# 获取实验详情
curl http://localhost:8000/api/v1/experiments/{experiment_id}

# 获取实验日志
curl http://localhost:8000/api/v1/experiments/{experiment_id}/logs

# 启动实验 (模拟)
curl -X POST http://localhost:8000/api/v1/experiments/{experiment_id}/start

# 停止实验 (模拟)
curl -X POST http://localhost:8000/api/v1/experiments/{experiment_id}/stop
```

### 4. Evaluations API

```bash
# 获取评测列表
curl http://localhost:8000/api/v1/evaluations

# 过滤: 只看spoken
curl "http://localhost:8000/api/v1/evaluations?track=spoken"

# 过滤: 只看written
curl "http://localhost:8000/api/v1/evaluations?track=written"

# 获取评测详情
curl http://localhost:8000/api/v1/evaluations/{evaluation_id}

# 获取实验的评测摘要 (spoken/written对比)
curl http://localhost:8000/api/v1/evaluations/experiment/{experiment_id}/summary
```

## 🎨 前端联调测试

### 1. 启动后端

```bash
# 在Veri-Train目录
cd /home/sharp/AI/VeriAI/Veri-Train
uvicorn app.main:app --reload --port 8000
```

### 2. 启动前端

```bash
# 在Veri-Train-UI目录
cd /home/sharp/AI/VeriAI/Veri-Train-UI
npm run dev
```

### 3. 访问测试

打开浏览器访问: http://localhost:3000

**测试路径**:
1. **Dashboard** (`/`) - 应该显示系统概览
2. **Models** (`/models`) - 应该显示12个模型
3. **Datasets** (`/datasets`) - 应该显示20个数据集
4. **Experiments** (`/experiments`) - 应该显示15个实验
5. **Evaluation** (`/evaluation`) - 应该显示20个评测结果

**前端应该能够**:
- ✅ 从API获取数据并展示
- ✅ 使用过滤器筛选数据
- ✅ 分页浏览数据
- ✅ 点击详情查看完整信息

## 🔍 验证要点

### 1. API响应格式

所有列表API返回标准分页格式:
```json
{
  "items": [...],
  "total": 20,
  "page": 1,
  "page_size": 20,
  "total_pages": 1
}
```

### 2. 数据完整性

- ✅ Models: 包含 baseline_probe, metadata_, config
- ✅ Datasets: 包含 overview, quality_gate_result, usage_history
- ✅ Experiments: 包含 config, progress (running时), logs, metrics (completed时)
- ✅ Evaluations: 包含 metrics, error_analysis, sample_results

### 3. 过滤功能

每个API都支持相应的过滤参数:
- Models: `status`, `type`, `search`
- Datasets: `status`, `type`, `scene`, `direction`, `search`
- Experiments: `status`, `model_id`, `search`
- Evaluations: `track`, `experiment_id`

## 🐛 常见问题

### Q1: 启动后API返回500错误

**原因**: 可能是某些依赖缺失

**解决**:
```bash
uv sync
```

### Q2: 前端无法连接后端

**检查**:
1. 后端是否在 8000 端口运行?
   ```bash
   curl http://localhost:8000/health
   ```

2. 前端环境变量是否正确?
   ```bash
   # Veri-Train-UI/.env
   VITE_API_BASE_URL=http://localhost:8000
   ```

3. CORS是否启用?
   - 后端已配置允许 `http://localhost:3000`

### Q3: 数据每次启动都不一样?

**说明**: 这是正常的！mock数据使用 `random` 生成，每次启动会重新生成。

**固定数据** (可选):
在各API文件中设置 `random.seed(42)` 即可获得固定数据。

## 📊 预期结果

### Dashboard
- 应显示系统概览
- 显示最近实验 (从experiments API获取)
- 显示最新数据集 (从datasets API获取)
- 显示系统告警

### Models 页面
- 列表显示 12 个模型
- 可按 type (base/adapter) 过滤
- 可按 status (available/training/deprecated) 过滤
- 点击可查看详情 (baseline_probe, prompt_contracts)

### Datasets 页面
- 列表显示 20 个数据集
- 可按 status (draft/passed/blocked) 过滤
- 可按 type (human/synthetic/mixed) 过滤
- 可按 scene (meeting/written) 过滤
- 点击可查看详情 (quality_gate, overview)

### Experiments 页面
- 列表显示 15 个实验
- 可按 status (pending/running/completed/failed) 过滤
- running状态显示进度条
- completed状态显示最终指标
- 点击可查看详情 (config, logs, metrics)

### Evaluation 页面
- 列表显示 20 个评测
- 可按 track (spoken/written) 过滤
- 显示 BLEU, ROUGE-L, RIBES 指标
- 点击可查看详情 (error_analysis, sample_results)

## 🎯 下一步

1. ✅ 所有API已完成假数据
2. ⏳ 前端页面完善 (详情页、图表)
3. ⏳ WebSocket实时通信
4. ⏳ 文件上传功能
5. ⏳ 认证系统

---

**现在可以立即测试前后端联调！无需任何数据库配置！**

```bash
# 终端1: 启动后端
cd Veri-Train
uv run uvicorn app.main:app --reload

# 终端2: 启动前端
cd Veri-Train-UI
npm run dev

# 浏览器: 访问 http://localhost:3000
```
