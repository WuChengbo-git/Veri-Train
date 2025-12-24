"""
Celery应用配置
"""

from celery import Celery
from app.config import settings

# 创建Celery应用
celery_app = Celery(
    "veri_train",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.training",
        "app.tasks.generation",
        "app.tasks.evaluation",
        "app.tasks.quality_gate",
    ],
)

# Celery配置
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600 * 4,  # 4小时超时
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
)


if __name__ == "__main__":
    celery_app.start()
