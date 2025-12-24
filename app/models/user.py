"""
User相关数据库模型
"""

from sqlalchemy import Column, String, Boolean
from app.models.base import Base


class User(Base):
    """用户表"""

    __tablename__ = "users"

    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    avatar = Column(String(500), nullable=True)
