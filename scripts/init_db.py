"""
数据库初始化脚本
"""

from app.database import engine
from app.models import Base
import structlog

logger = structlog.get_logger()


def init_db():
    """创建所有数据库表"""
    logger.info("Initializing database...")

    # 创建所有表
    Base.metadata.create_all(bind=engine)

    logger.info("Database initialized successfully!")


if __name__ == "__main__":
    init_db()
