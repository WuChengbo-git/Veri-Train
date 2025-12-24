"""
配置管理 - 使用Pydantic Settings
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """应用配置"""

    # API配置
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Veri-Train API"
    DEBUG: bool = False

    # 数据库
    DATABASE_URL: str

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # Azure OpenAI
    AZURE_OPENAI_KEY: str
    AZURE_OPENAI_ENDPOINT: str
    AZURE_OPENAI_DEPLOYMENT: str = "gpt-4"
    AZURE_OPENAI_API_VERSION: str = "2024-02-15-preview"

    # JWT认证
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000"

    @property
    def allowed_origins_list(self) -> List[str]:
        """将CORS origin字符串转换为列表"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    # 文件存储
    UPLOAD_DIR: str = "./uploads"
    CHECKPOINT_DIR: str = "./checkpoints"
    DATASET_DIR: str = "./datasets"

    # Quality Gate阈值
    QUALITY_GATE_ALIGNMENT_RATE: float = 0.8
    QUALITY_GATE_DUPLICATE_RATE: float = 0.2
    QUALITY_GATE_LANGUAGE_CONSISTENCY: float = 0.9

    class Config:
        env_file = ".env"
        case_sensitive = True


# 全局配置实例
settings = Settings()
