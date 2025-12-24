"""
Evaluation相关数据库模型
"""

from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.models.base import Base


class Evaluation(Base):
    """评测表"""

    __tablename__ = "evaluations"

    experiment_id = Column(UUID(as_uuid=True), ForeignKey("experiments.id"), nullable=False)
    track = Column(String(50), nullable=False)  # 'spoken' | 'written'

    # 评测指标(JSONB格式)
    metrics = Column(JSONB, nullable=False, default=dict)
    # {
    #   "bleu": 0.45,
    #   "rouge_l": 0.52,
    #   "ribes": 0.78,
    #   "gpt_eval_1": {
    #     "fluency": 4.2,
    #     "adequacy": 4.0,
    #     "accuracy": 4.1
    #   },
    #   "gpt_eval_2": {
    #     "mqm_score": 85.5,
    #     "error_distribution": [...]
    #   }
    # }

    # 错误分析
    error_analysis = Column(JSONB, default=dict)
    # {
    #   "top_errors": [...],
    #   "error_type_distribution": {...}
    # }

    # 关系
    experiment = relationship("Experiment", back_populates="evaluations")
