# Veri-Train Backend API

Veri-Train模型迭代闭环工作台 - 后端API服务

## 概要

这是Veri-Train系统的后端服务,提供:
- RESTful API (FastAPI)
- 异步任务队列 (Celery)
- 实时通信 (WebSocket)
- 数据库管理 (PostgreSQL)

## 技术栈

- **FastAPI 0.109** - 高性能Web框架
- **SQLAlchemy 2.0** - ORM
- **PostgreSQL 15** - 主数据库
- **Celery 5.3** - 异步任务队列
- **Redis 7** - 缓存 & 消息代理
- **Pydantic 2.5** - 数据验证
- **Alembic** - 数据库迁移

## 快速开始

### 使用Docker Compose (推荐)

```bash
# 1. 复制环境变量
cp .env.example .env

# 2. 编辑.env,配置必要的环境变量
# 特别是AZURE_OPENAI_KEY等

# 3. 启动所有服务
docker-compose up -d

# 4. 查看日志
docker-compose logs -f api

# 5. 初始化数据库
docker-compose exec api python scripts/init_db.py
```

服务访问:
- **API文档**: http://localhost:8000/api/v1/docs
- **Flower监控**: http://localhost:5555

### 本地开发

```bash
# 1. 创建虚拟环境
python3.11 -m venv venv
source venv/bin/activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动PostgreSQL和Redis
docker-compose up -d postgres redis

# 4. 配置环境变量
cp .env.example .env
# 编辑.env

# 5. 初始化数据库
python scripts/init_db.py

# 6. 启动FastAPI
uvicorn app.main:app --reload

# 7. 启动Celery Worker (另开终端)
celery -A app.tasks.celery_app worker --loglevel=info

# 8. (可选) 启动Flower监控
celery -A app.tasks.celery_app flower
```

## 项目结构

```
app/
├── api/
│   └── v1/
│       ├── endpoints/       # API路由
│       │   ├── models.py    # Models API
│       │   ├── datasets.py  # Datasets API
│       │   └── experiments.py
│       ├── deps.py          # 依赖注入
│       └── router.py        # 路由聚合
├── models/                  # SQLAlchemy模型
│   ├── model.py
│   ├── dataset.py
│   ├── experiment.py
│   ├── evaluation.py
│   └── report.py
├── schemas/                 # Pydantic Schemas
│   ├── model.py
│   ├── common.py
│   └── ...
├── services/                # 业务逻辑层
│   └── model_service.py
├── tasks/                   # Celery任务
│   ├── celery_app.py
│   ├── training.py          # ⭐ 训练任务
│   ├── quality_gate.py      # ⭐ 质量门禁
│   ├── generation.py
│   └── evaluation.py
├── core/                    # 核心功能
├── utils/                   # 工具函数
├── config.py                # 配置管理
├── database.py              # 数据库连接
└── main.py                  # FastAPI入口
```

## 核心功能

### 1. Models API

```bash
# 获取模型列表
GET /api/v1/models?page=1&page_size=20

# 获取模型详情
GET /api/v1/models/{model_id}

# ⭐ 运行Baseline Probe(关键功能)
POST /api/v1/models/{model_id}/probe

# 创建模型
POST /api/v1/models

# 更新模型状态
PATCH /api/v1/models/{model_id}/status
```

**Baseline Probe** 是系统的核心创新功能,用于检测模型的基础能力:
- 是否支持多候选输出
- 是否提供解释性输出
- 是否遵循输出契约

### 2. Datasets API

```bash
# 获取数据集列表
GET /api/v1/datasets

# 上传数据集
POST /api/v1/datasets

# ⭐ 生成数据集
POST /api/v1/datasets/generate

# 获取Quality Gate结果
GET /api/v1/datasets/{dataset_id}/quality-gate
```

### 3. Experiments API

```bash
# 获取实验列表
GET /api/v1/experiments

# 创建实验
POST /api/v1/experiments

# 启动实验
POST /api/v1/experiments/{experiment_id}/start

# 获取实验日志
GET /api/v1/experiments/{experiment_id}/logs

# WebSocket实时进度
WS /api/v1/experiments/{experiment_id}/stream
```

## 数据库迁移

```bash
# 创建新的迁移
alembic revision --autogenerate -m "描述"

# 执行迁移
alembic upgrade head

# 回滚
alembic downgrade -1
```

## Celery任务

### 训练任务

```python
from app.tasks.training import train_model

# 异步启动训练
task = train_model.delay(experiment_id="xxx")

# 检查任务状态
result = task.get()
```

### Quality Gate任务

```python
from app.tasks.quality_gate import check_quality_gate

# 检查数据质量
task = check_quality_gate.delay(dataset_id="xxx")
```

## 环境变量说明

```env
# 数据库
DATABASE_URL=postgresql://user:pass@host:port/dbname

# Redis
REDIS_URL=redis://localhost:6379/0

# Azure OpenAI (用于数据生成和评测)
AZURE_OPENAI_KEY=your-key
AZURE_OPENAI_ENDPOINT=https://xxx.openai.azure.com

# JWT认证
SECRET_KEY=your-secret-key

# CORS
ALLOWED_ORIGINS=http://localhost:3000
```

## 开发指南

### 添加新的API Endpoint

1. 在`app/api/v1/endpoints/`创建新文件
2. 定义路由和处理函数
3. 在`app/api/v1/router.py`中注册路由

### 添加新的Celery任务

1. 在`app/tasks/`创建新文件
2. 使用`@celery_app.task`装饰器
3. 在`app/tasks/celery_app.py`的include中添加

### 添加新的数据库模型

1. 在`app/models/`创建模型类
2. 从`app.models.base.Base`继承
3. 创建对应的Pydantic Schema
4. 生成迁移: `alembic revision --autogenerate -m "add xxx"`

## 测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/api/test_models.py

# 生成覆盖率报告
pytest --cov=app --cov-report=html
```

## 监控

### Flower (Celery监控)

访问 http://localhost:5555 查看:
- 活跃的Worker
- 任务执行历史
- 任务成功/失败统计

### 日志

使用structlog进行结构化日志:

```python
import structlog
logger = structlog.get_logger()

logger.info("event_name", key1="value1", key2="value2")
```

## 部署

### 生产环境配置

1. 修改`.env`中的密钥和密码
2. 设置`DEBUG=False`
3. 配置HTTPS
4. 使用Gunicorn运行FastAPI:

```bash
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### Docker部署

```bash
# 构建镜像
docker build -t veritrain-api .

# 运行
docker-compose -f docker-compose.prod.yml up -d
```

## API文档

启动服务后访问:
- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc

## 故障排查

### 数据库连接失败

```bash
# 检查PostgreSQL是否运行
docker-compose ps postgres

# 查看日志
docker-compose logs postgres
```

### Celery任务不执行

```bash
# 检查Worker状态
celery -A app.tasks.celery_app inspect active

# 查看Worker日志
docker-compose logs celery_worker
```

### Redis连接失败

```bash
# 测试Redis连接
redis-cli -h localhost -p 6379 ping
```

## 下一步开发

**高优先级** (核心功能):
1. ✅ Models API - 已实现基础框架
2. ⏳ Datasets API - 需实现上传和Quality Gate
3. ⏳ Experiments API - 需实现训练流程
4. ⏳ WebSocket服务 - 实时进度推送

**中优先级** (重要功能):
5. ⏳ Evaluation API - 评测结果管理
6. ⏳ Reports API - 报告生成
7. ⏳ 认证系统 - JWT完整实现

**低优先级** (优化):
8. ⏳ 单元测试覆盖
9. ⏳ API限流
10. ⏳ 监控告警

## 与前端集成

前端项目位于 `../Veri-Train-UI/`

确保:
1. API端口8000和前端代理配置一致
2. CORS配置包含前端URL
3. WebSocket端点正确配置

## 贡献指南

1. Fork项目
2. 创建特性分支
3. 提交变更
4. 推送到分支
5. 创建Pull Request

## 许可证

MIT

## 联系方式

如有问题,请创建Issue。
