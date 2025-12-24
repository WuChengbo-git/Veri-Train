"""
评测任务 (Placeholder)
"""

from app.tasks.celery_app import celery_app


@celery_app.task(name="evaluate_model")
def evaluate_model(experiment_id: str):
    """
    模型评测任务 (TODO: 完整实现)
    """
    return {"status": "completed", "experiment_id": experiment_id}
