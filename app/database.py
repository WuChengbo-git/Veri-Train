"""
数据库连接和Session管理
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# 创建数据库引擎
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # 连接池预检测
    echo=settings.DEBUG,  # SQL日志
)

# Session工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 声明式基类
Base = declarative_base()


def get_db():
    """
    数据库Session依赖注入
    用于FastAPI路由中获取数据库连接
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
