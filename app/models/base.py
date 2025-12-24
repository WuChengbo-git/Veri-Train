"""
基础模型类
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base as SQLAlchemyBase


class Base(SQLAlchemyBase):
    """抽象基类,所有模型继承此类"""

    __abstract__ = True

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def dict(self):
        """转换为字典"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
