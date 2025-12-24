"""
Model相关数据库模型
"""

from sqlalchemy import Column, String, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.models.base import Base


class Model(Base):
    """模型表"""

    __tablename__ = "models"

    name = Column(String(255), nullable=False, index=True)
    type = Column(String(50), nullable=False)  # 'base' | 'adapter'
    base_model_id = Column(UUID(as_uuid=True), ForeignKey("models.id"), nullable=True)
    status = Column(String(50), default="available")  # 'available' | 'deprecated' | 'training'

    # 配置信息(JSONB格式)
    config = Column(JSONB, nullable=False, default=dict)

    # 元数据
    metadata_ = Column("metadata", JSONB, default=dict)  # parameters, tokenizer, source

    # Baseline Probe结果
    baseline_probe = Column(JSONB, nullable=True)

    # 关系
    base_model = relationship("Model", remote_side="Model.id", backref="adapters")
    prompt_contracts = relationship("PromptContract", back_populates="model")


class PromptContract(Base):
    """Prompt契约表"""

    __tablename__ = "prompt_contracts"

    name = Column(String(255), nullable=False)
    version = Column(Integer, default=1)
    template = Column(String, nullable=False)
    model_id = Column(UUID(as_uuid=True), ForeignKey("models.id"), nullable=False)

    # 关系
    model = relationship("Model", back_populates="prompt_contracts")
