"""
Models API endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID

from app.api.v1.deps import get_db, get_current_user
from app.models.model import Model as DBModel
from app.models.user import User
from app.schemas.model import Model, ModelDetail, ModelCreate, RunProbeRequest, BaselineProbe
from app.schemas.common import PaginatedResponse
from app.services.model_service import ModelService

router = APIRouter()


@router.get("", response_model=PaginatedResponse[Model])
async def get_models(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    type: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    モデル一覧を取得
    """
    service = ModelService(db)
    return service.get_models(
        page=page, page_size=page_size, status=status, model_type=type
    )


@router.get("/{model_id}", response_model=ModelDetail)
async def get_model_detail(
    model_id: UUID,
    db: Session = Depends(get_db),
):
    """
    モデル詳細を取得
    """
    service = ModelService(db)
    model = service.get_model_by_id(model_id)
    if not model:
        raise HTTPException(status_code=404, detail="モデルが見つかりません")
    return model


@router.post("", response_model=Model, status_code=201)
async def create_model(
    model_data: ModelCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    新規モデルを作成
    """
    service = ModelService(db)
    return service.create_model(model_data)


@router.post("/{model_id}/probe", response_model=BaselineProbe)
async def run_baseline_probe(
    model_id: UUID,
    request: RunProbeRequest = RunProbeRequest(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    ベースライン動作探査を実行

    このエンドポイントは重要な機能:
    - モデルが多候補出力をサポートするか
    - 説明性出力を提供するか
    - 出力契約に従うか
    """
    service = ModelService(db)
    model = service.get_model_by_id(model_id)
    if not model:
        raise HTTPException(status_code=404, detail="モデルが見つかりません")

    # 探査実行
    probe_result = service.run_baseline_probe(model_id, request.test_cases)
    return probe_result


@router.get("/{model_id}/evaluations")
async def get_model_evaluations(
    model_id: UUID,
    db: Session = Depends(get_db),
):
    """
    モデルの評価履歴を取得
    """
    service = ModelService(db)
    return service.get_model_evaluations(model_id)


@router.patch("/{model_id}/status", response_model=Model)
async def update_model_status(
    model_id: UUID,
    status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    モデルステータスを更新
    """
    service = ModelService(db)
    model = service.update_model_status(model_id, status)
    if not model:
        raise HTTPException(status_code=404, detail="モデルが見つかりません")
    return model


@router.delete("/{model_id}", status_code=204)
async def delete_model(
    model_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    モデルを削除
    """
    service = ModelService(db)
    success = service.delete_model(model_id)
    if not success:
        raise HTTPException(status_code=404, detail="モデルが見つかりません")
