"""
Datasets API endpoints (Placeholder)
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def get_datasets():
    """データセット一覧を取得 (TODO: 実装)"""
    return {"items": [], "total": 0}


@router.post("")
async def create_dataset():
    """データセットを作成 (TODO: 実装)"""
    return {"message": "実装中"}


@router.post("/generate")
async def generate_dataset():
    """データセットを生成 (TODO: 実装)"""
    return {"task_id": "placeholder"}
