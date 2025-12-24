"""
Experiment相关数据库模型
"""

from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.models.base import Base


class Experiment(Base):
    """实验表"""

    __tablename__ = "experiments"

    name = Column(String(255), nullable=False, index=True)
    task = Column(String(50), default="translation")
    direction = Column(String(20), nullable=False)  # 'ja-en', 'en-ja'

    # 关联外键
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id"), nullable=False)
    base_model_id = Column(UUID(as_uuid=True), ForeignKey("models.id"), nullable=False)
    adapter_id = Column(UUID(as_uuid=True), ForeignKey("models.id"), nullable=True)
    prompt_contract_id = Column(
        UUID(as_uuid=True), ForeignKey("prompt_contracts.id"), nullable=True
    )

    # 配置(JSONB格式)
    config = Column(JSONB, nullable=False, default=dict)
    # {
    #   "dataset_version": 1,
    #   "training_recipe": {
    #     "lora_config": {...},
    #     "batch_size": 16,
    #     "learning_rate": 1e-4,
    #     "epochs": 10
    #   },
    #   "seed": 42,
    #   "environment": {}
    # }

    # 状态
    status = Column(String(50), default="pending")
    # 'pending' | 'running' | 'completed' | 'failed' | 'stopped'

    # 结果
    metrics = Column(JSONB, nullable=True)
    best_checkpoint_path = Column(String(500), nullable=True)

    # Celery任务ID
    celery_task_id = Column(String(255), nullable=True)

    # 时间戳
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # 关系
    dataset = relationship("Dataset", back_populates="experiments")
    base_model = relationship("Model", foreign_keys=[base_model_id])
    adapter = relationship("Model", foreign_keys=[adapter_id])
    evaluations = relationship("Evaluation", back_populates="experiment")
