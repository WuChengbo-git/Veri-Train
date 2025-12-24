"""
Experiments API endpoints (Placeholder)
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def get_experiments():
    """実験一覧を取得 (TODO: 実装)"""
    return {"items": [], "total": 0}


@router.post("")
async def create_experiment():
    """実験を作成 (TODO: 実装)"""
    return {"message": "実装中"}


@router.post("/{experiment_id}/start")
async def start_experiment(experiment_id: str):
    """実験を開始 (TODO: 実装)"""
    return {"status": "started"}
