"""
数据生成任务 (Placeholder)
"""

from app.tasks.celery_app import celery_app


@celery_app.task(name="generate_dataset")
def generate_dataset(config: dict):
    """
    数据集生成任务 (TODO: 完整实现)
    """
    return {"status": "completed", "dataset_id": "placeholder"}
