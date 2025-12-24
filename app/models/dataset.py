"""
Dataset相关数据库模型
"""

from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.models.base import Base


class Dataset(Base):
    """数据集表"""

    __tablename__ = "datasets"

    name = Column(String(255), nullable=False, index=True)
    version = Column(Integer, default=1)
    type = Column(String(50), nullable=False)  # 'human' | 'synthetic' | 'mixed'
    language_direction = Column(String(20), nullable=False)  # 'ja-en', 'en-ja'
    scene = Column(String(50), nullable=False)  # 'meeting' | 'written'
    status = Column(String(50), default="draft")  # 'draft' | 'passed' | 'blocked'

    # 父数据集ID(用于版本管理)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id"), nullable=True)

    # 数据集概览信息
    overview = Column(JSONB, default=dict)
    # {
    #   "total_count": 1000,
    #   "avg_sentence_length": 25.5,
    #   "short_sentence_ratio": 0.3,
    #   "code_switch_ratio": 0.05
    # }

    # Quality Gate结果
    quality_gate_result = Column(JSONB, nullable=True)
    # {
    #   "status": "passed",
    #   "checked_at": "2024-01-01T00:00:00Z",
    #   "metrics": {
    #     "alignment_rate": 0.95,
    #     "duplicate_rate": 0.05,
    #     "language_consistency": 0.98
    #   },
    #   "sampling_review": {...}
    # }

    # 文件路径
    file_path = Column(String(500), nullable=True)

    # 关系
    parent = relationship("Dataset", remote_side="Dataset.id", backref="versions")
    experiments = relationship("Experiment", back_populates="dataset")
