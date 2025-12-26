"""
Experiment相关Schema定义
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from app.schemas.common import BaseSchema


class TrainingRecipe(BaseModel):
    """训练配方"""

    lora_config: Optional[Dict[str, Any]] = None
    batch_size: int = 16
    learning_rate: float = 1e-4
    epochs: int = 10
    warmup_steps: int = 100
    optimizer: str = "adamw"


class ExperimentConfig(BaseModel):
    """实验配置"""

    dataset_version: int = 1
    prompt_contract_id: Optional[UUID] = None
    training_recipe: TrainingRecipe
    seed: int = 42
    environment: Dict[str, Any] = {}


class ExperimentBase(BaseModel):
    """Experiment基础"""

    name: str
    task: str = "translation"
    direction: str
    dataset_id: UUID
    base_model_id: UUID
    adapter_id: Optional[UUID] = None


class ExperimentCreate(ExperimentBase):
    """创建Experiment"""

    config: ExperimentConfig


class Experiment(ExperimentBase, BaseSchema):
    """Experiment完整信息"""

    status: str = "pending"
    best_score: Optional[float] = None
    celery_task_id: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class ExperimentProgress(BaseModel):
    """实验进度"""

    current_epoch: int
    total_epochs: int
    current_step: int
    total_steps: int
    loss: float
    gpu_utilization: float
    eta: str
    last_update: str


class LogEntry(BaseModel):
    """日志条目"""

    timestamp: str
    level: str  # 'info' | 'warning' | 'error'
    message: str


class ExperimentDetail(Experiment):
    """Experiment详情"""

    config: Optional[Dict[str, Any]] = None
    progress: Optional[ExperimentProgress] = None
    logs: List[LogEntry] = []
    metrics: Optional[Dict[str, Any]] = None
