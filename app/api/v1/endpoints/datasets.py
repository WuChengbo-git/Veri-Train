"""
Datasets API endpoints (with mock data)
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID, uuid4
from datetime import datetime, timedelta
import random

from app.api.v1.deps import get_db
from app.schemas.dataset import (
    Dataset,
    DatasetDetail,
    DatasetCreate,
    GenerateDatasetConfig,
    GenerateEstimate,
    DatasetOverview,
    QualityGateResult,
    QualityGateMetrics,
)
from app.schemas.common import PaginatedResponse, TaskResponse

router = APIRouter()

# 假数据生成器
def generate_mock_datasets(count: int = 20) -> list:
    """生成模拟数据集"""
    datasets = []
    types = ["human", "synthetic", "mixed"]
    directions = ["ja-en", "en-ja"]
    scenes = ["meeting", "written"]
    statuses = ["draft", "passed", "blocked"]

    for i in range(count):
        dataset = {
            "id": str(uuid4()),
            "name": f"dataset-{random.choice(directions)}-{random.choice(scenes)}-v{random.randint(1,5)}",
            "type": random.choice(types),
            "language_direction": random.choice(directions),
            "scene": random.choice(scenes),
            "status": random.choice(statuses),
            "version": random.randint(1, 5),
            "parent_id": None,
            "file_path": f"/datasets/{uuid4()}.jsonl",
            "created_at": (datetime.utcnow() - timedelta(days=random.randint(1, 30))).isoformat(),
            "updated_at": (datetime.utcnow() - timedelta(hours=random.randint(1, 24))).isoformat(),
        }
        datasets.append(dataset)

    return datasets


# 全局模拟数据
MOCK_DATASETS = generate_mock_datasets(20)


@router.get("", response_model=PaginatedResponse[Dataset])
async def get_datasets(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    type: Optional[str] = None,
    scene: Optional[str] = None,
    direction: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    データセット一覧を取得
    """
    # 过滤
    filtered = MOCK_DATASETS.copy()

    if status:
        filtered = [d for d in filtered if d["status"] == status]
    if type:
        filtered = [d for d in filtered if d["type"] == type]
    if scene:
        filtered = [d for d in filtered if d["scene"] == scene]
    if direction:
        filtered = [d for d in filtered if d["language_direction"] == direction]
    if search:
        filtered = [d for d in filtered if search.lower() in d["name"].lower()]

    # 分页
    total = len(filtered)
    start = (page - 1) * page_size
    end = start + page_size
    items = filtered[start:end]

    total_pages = (total + page_size - 1) // page_size

    return PaginatedResponse(
        items=items, total=total, page=page, page_size=page_size, total_pages=total_pages
    )


@router.get("/{dataset_id}", response_model=DatasetDetail)
async def get_dataset_detail(
    dataset_id: str,
    db: Session = Depends(get_db),
):
    """
    データセット詳細を取得
    """
    # 查找数据集
    dataset = next((d for d in MOCK_DATASETS if d["id"] == dataset_id), None)
    if not dataset:
        raise HTTPException(status_code=404, detail="データセットが見つかりません")

    # 生成详细信息
    detail = {
        **dataset,
        "overview": {
            "total_count": random.randint(500, 10000),
            "avg_sentence_length": round(random.uniform(15.0, 35.0), 1),
            "short_sentence_ratio": round(random.uniform(0.1, 0.4), 2),
            "code_switch_ratio": round(random.uniform(0.0, 0.15), 2),
        },
        "quality_gate_result": {
            "status": dataset["status"] if dataset["status"] != "draft" else "passed",
            "checked_at": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
            "metrics": {
                "alignment_rate": round(random.uniform(0.75, 0.98), 2),
                "duplicate_rate": round(random.uniform(0.02, 0.25), 2),
                "language_consistency": round(random.uniform(0.85, 0.99), 2),
            },
            "block_reasons": (
                ["対齐率が低い: 0.75 < 0.80"] if dataset["status"] == "blocked" else None
            ),
        },
        "usage_history": [
            {
                "experiment_id": str(uuid4()),
                "experiment_name": f"exp-{random.randint(1000,9999)}",
                "used_at": (datetime.utcnow() - timedelta(days=i)).isoformat(),
                "performance": round(random.uniform(0.3, 0.8), 2),
            }
            for i in range(3)
        ],
    }

    return detail


@router.post("", response_model=Dataset, status_code=201)
async def create_dataset(
    dataset_data: DatasetCreate,
    db: Session = Depends(get_db),
):
    """
    データセットを作成
    """
    new_dataset = {
        "id": str(uuid4()),
        "name": dataset_data.name,
        "type": dataset_data.type,
        "language_direction": dataset_data.language_direction,
        "scene": dataset_data.scene,
        "status": "draft",
        "version": dataset_data.version,
        "parent_id": str(dataset_data.parent_id) if dataset_data.parent_id else None,
        "file_path": f"/datasets/{uuid4()}.jsonl",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }

    MOCK_DATASETS.insert(0, new_dataset)
    return new_dataset


@router.post("/generate/estimate", response_model=GenerateEstimate)
async def estimate_generation(
    config: GenerateDatasetConfig,
    db: Session = Depends(get_db),
):
    """
    データセット生成のコスト見積もり
    """
    # 简单估算
    total_tokens = config.target_count * 200  # 假设每条200 tokens
    cost_per_1k = 0.03  # $0.03/1K tokens
    estimated_cost = (total_tokens / 1000) * cost_per_1k
    estimated_time = f"{config.target_count // 100}分"

    return GenerateEstimate(
        total_tokens=total_tokens,
        estimated_cost=round(estimated_cost, 2),
        estimated_time=estimated_time,
    )


@router.post("/generate", response_model=TaskResponse)
async def generate_dataset(
    config: GenerateDatasetConfig,
    db: Session = Depends(get_db),
):
    """
    データセットを生成 (非同期タスク)
    """
    # TODO: 触发Celery任务
    task_id = str(uuid4())

    return TaskResponse(
        task_id=task_id, status="started", message="データセット生成タスクが開始されました"
    )


@router.get("/{dataset_id}/quality-gate", response_model=QualityGateResult)
async def get_quality_gate(
    dataset_id: str,
    db: Session = Depends(get_db),
):
    """
    Quality Gate結果を取得
    """
    dataset = next((d for d in MOCK_DATASETS if d["id"] == dataset_id), None)
    if not dataset:
        raise HTTPException(status_code=404, detail="データセットが見つかりません")

    return QualityGateResult(
        status=dataset["status"] if dataset["status"] != "draft" else "passed",
        checked_at=(datetime.utcnow() - timedelta(hours=1)).isoformat(),
        metrics=QualityGateMetrics(
            alignment_rate=round(random.uniform(0.75, 0.98), 2),
            duplicate_rate=round(random.uniform(0.02, 0.25), 2),
            language_consistency=round(random.uniform(0.85, 0.99), 2),
        ),
        block_reasons=(
            ["重複率が高い: 0.25 > 0.20"] if dataset["status"] == "blocked" else None
        ),
    )


@router.delete("/{dataset_id}", status_code=204)
async def delete_dataset(
    dataset_id: str,
    db: Session = Depends(get_db),
):
    """
    データセットを削除
    """
    global MOCK_DATASETS
    MOCK_DATASETS = [d for d in MOCK_DATASETS if d["id"] != dataset_id]
