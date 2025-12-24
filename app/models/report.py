"""
Report相关数据库模型
"""

from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.models.base import Base


class Report(Base):
    """报告表"""

    __tablename__ = "reports"

    experiment_id = Column(UUID(as_uuid=True), ForeignKey("experiments.id"), nullable=False)
    title = Column(String(255), nullable=False)
    status = Column(String(50), default="draft")  # 'draft' | 'published'

    # 报告内容(JSONB格式)
    summary = Column(JSONB, default=dict)
    # {
    #   "changes": [...],
    #   "improvements": [...],
    #   "regressions": [...]
    # }

    comparison = Column(JSONB, default=dict)
    # {
    #   "baseline_experiment_id": "...",
    #   "current_experiment_id": "...",
    #   "differences": {...}
    # }

    synthetic_data_analysis = Column(JSONB, default=dict)
    # {
    #   "synthetic_ratio": 0.3,
    #   "performance_change": 0.05,
    #   "quality_assessment": "...",
    #   "recommendation": "..."
    # }

    next_steps = Column(JSONB, default=list)  # ["step1", "step2", ...]

    # 发布时间
    published_at = Column(DateTime, nullable=True)

    # 关系
    experiment = relationship("Experiment")
