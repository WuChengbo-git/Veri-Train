"""
Experiments API endpoints (with mock data)
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime, timedelta
import random

from app.api.v1.deps import get_db
from app.schemas.experiment import (
    Experiment,
    ExperimentDetail,
    ExperimentCreate,
    ExperimentProgress,
    LogEntry,
)
from app.schemas.common import PaginatedResponse, TaskResponse

router = APIRouter()


# 假数据生成器
def generate_mock_experiments(count: int = 15) -> list:
    """生成模拟实验"""
    experiments = []
    statuses = ["pending", "running", "completed", "failed"]
    directions = ["ja-en", "en-ja"]

    for i in range(count):
        status = random.choice(statuses)
        created_time = datetime.utcnow() - timedelta(days=random.randint(1, 30))

        experiment = {
            "id": str(uuid4()),
            "name": f"exp-{random.choice(directions)}-{random.randint(1000, 9999)}",
            "task": "translation",
            "direction": random.choice(directions),
            "dataset_id": str(uuid4()),
            "base_model_id": str(uuid4()),
            "adapter_id": str(uuid4()) if random.random() > 0.5 else None,
            "status": status,
            "best_score": round(random.uniform(0.4, 0.85), 2) if status == "completed" else None,
            "celery_task_id": str(uuid4()) if status in ["running", "completed"] else None,
            "created_at": created_time.isoformat(),
            "updated_at": (created_time + timedelta(hours=random.randint(1, 48))).isoformat(),
            "started_at": (
                (created_time + timedelta(minutes=5)).isoformat()
                if status in ["running", "completed", "failed"]
                else None
            ),
            "completed_at": (
                (created_time + timedelta(hours=random.randint(2, 12))).isoformat()
                if status == "completed"
                else None
            ),
        }
        experiments.append(experiment)

    return experiments


# 全局模拟数据
MOCK_EXPERIMENTS = generate_mock_experiments(15)


@router.get("", response_model=PaginatedResponse[Experiment])
async def get_experiments(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    model_id: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    実験一覧を取得
    """
    # 过滤
    filtered = MOCK_EXPERIMENTS.copy()

    if status:
        filtered = [e for e in filtered if e["status"] == status]
    if model_id:
        filtered = [
            e for e in filtered if e["base_model_id"] == model_id or e["adapter_id"] == model_id
        ]
    if search:
        filtered = [e for e in filtered if search.lower() in e["name"].lower()]

    # 分页
    total = len(filtered)
    start = (page - 1) * page_size
    end = start + page_size
    items = filtered[start:end]

    total_pages = (total + page_size - 1) // page_size

    return PaginatedResponse(
        items=items, total=total, page=page, page_size=page_size, total_pages=total_pages
    )


@router.get("/{experiment_id}", response_model=ExperimentDetail)
async def get_experiment_detail(
    experiment_id: str,
    db: Session = Depends(get_db),
):
    """
    実験詳細を取得
    """
    # 查找实验
    experiment = next((e for e in MOCK_EXPERIMENTS if e["id"] == experiment_id), None)
    if not experiment:
        raise HTTPException(status_code=404, detail="実験が見つかりません")

    # 生成详细信息
    detail = {
        **experiment,
        "config": {
            "dataset_version": 1,
            "prompt_contract_id": str(uuid4()),
            "training_recipe": {
                "lora_config": {
                    "r": 8,
                    "alpha": 16,
                    "dropout": 0.1,
                    "target_modules": ["q_proj", "v_proj"],
                },
                "batch_size": 16,
                "learning_rate": 1e-4,
                "epochs": 10,
                "warmup_steps": 100,
                "optimizer": "adamw",
            },
            "seed": 42,
            "environment": {},
        },
        "progress": (
            {
                "current_epoch": random.randint(1, 10),
                "total_epochs": 10,
                "current_step": random.randint(100, 1000),
                "total_steps": 1000,
                "loss": round(random.uniform(0.3, 1.5), 3),
                "gpu_utilization": round(random.uniform(70.0, 95.0), 1),
                "eta": f"{random.randint(10, 120)}分",
                "last_update": datetime.utcnow().isoformat(),
            }
            if experiment["status"] == "running"
            else None
        ),
        "logs": [
            {
                "timestamp": (datetime.utcnow() - timedelta(minutes=i * 5)).isoformat(),
                "level": random.choice(["info", "info", "info", "warning"]),
                "message": random.choice(
                    [
                        "Training started",
                        f"Epoch {i+1}/10 completed",
                        f"Loss: {random.uniform(0.3, 1.5):.3f}",
                        "Checkpoint saved",
                        "GPU utilization: 85%",
                    ]
                ),
            }
            for i in range(10)
        ],
        "metrics": (
            {
                "final_loss": round(random.uniform(0.2, 0.5), 3),
                "best_bleu": round(random.uniform(0.4, 0.8), 2),
                "training_time": f"{random.randint(2, 12)}時間",
            }
            if experiment["status"] == "completed"
            else None
        ),
    }

    return detail


@router.post("", response_model=Experiment, status_code=201)
async def create_experiment(
    experiment_data: ExperimentCreate,
    db: Session = Depends(get_db),
):
    """
    実験を作成
    """
    new_experiment = {
        "id": str(uuid4()),
        "name": experiment_data.name,
        "task": experiment_data.task,
        "direction": experiment_data.direction,
        "dataset_id": str(experiment_data.dataset_id),
        "base_model_id": str(experiment_data.base_model_id),
        "adapter_id": str(experiment_data.adapter_id) if experiment_data.adapter_id else None,
        "status": "pending",
        "best_score": None,
        "celery_task_id": None,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "started_at": None,
        "completed_at": None,
    }

    MOCK_EXPERIMENTS.insert(0, new_experiment)
    return new_experiment


@router.post("/{experiment_id}/start", response_model=TaskResponse)
async def start_experiment(
    experiment_id: str,
    db: Session = Depends(get_db),
):
    """
    実験を開始
    """
    experiment = next((e for e in MOCK_EXPERIMENTS if e["id"] == experiment_id), None)
    if not experiment:
        raise HTTPException(status_code=404, detail="実験が見つかりません")

    if experiment["status"] != "pending":
        raise HTTPException(status_code=400, detail="この実験は既に開始されています")

    # 更新状态
    experiment["status"] = "running"
    experiment["started_at"] = datetime.utcnow().isoformat()
    experiment["celery_task_id"] = str(uuid4())

    return TaskResponse(
        task_id=experiment["celery_task_id"],
        status="started",
        message="実験が開始されました",
    )


@router.post("/{experiment_id}/stop", response_model=Experiment)
async def stop_experiment(
    experiment_id: str,
    db: Session = Depends(get_db),
):
    """
    実験を停止
    """
    experiment = next((e for e in MOCK_EXPERIMENTS if e["id"] == experiment_id), None)
    if not experiment:
        raise HTTPException(status_code=404, detail="実験が見つかりません")

    if experiment["status"] != "running":
        raise HTTPException(status_code=400, detail="実行中の実験ではありません")

    # 更新状态
    experiment["status"] = "stopped"
    experiment["completed_at"] = datetime.utcnow().isoformat()

    return experiment


@router.get("/{experiment_id}/logs")
async def get_experiment_logs(
    experiment_id: str,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """
    実験ログを取得
    """
    experiment = next((e for e in MOCK_EXPERIMENTS if e["id"] == experiment_id), None)
    if not experiment:
        raise HTTPException(status_code=404, detail="実験が見つかりません")

    # 生成日志
    logs = [
        {
            "timestamp": (datetime.utcnow() - timedelta(minutes=i * 5)).isoformat(),
            "level": random.choice(["info", "info", "info", "warning", "error"]),
            "message": random.choice(
                [
                    "Training initialization started",
                    "Loading dataset...",
                    "Loading model weights...",
                    f"Epoch {i%10 + 1}/10, Step {i*10 + 1}/1000",
                    f"Loss: {random.uniform(0.3, 1.5):.3f}",
                    "Saving checkpoint...",
                    f"GPU Memory: {random.randint(8000, 12000)}MB / 16384MB",
                    "Validation started",
                    f"Validation BLEU: {random.uniform(0.3, 0.7):.2f}",
                ]
            ),
        }
        for i in range(limit)
    ]

    return {"logs": logs[offset : offset + limit], "total": len(logs)}


@router.delete("/{experiment_id}", status_code=204)
async def delete_experiment(
    experiment_id: str,
    db: Session = Depends(get_db),
):
    """
    実験を削除
    """
    global MOCK_EXPERIMENTS
    MOCK_EXPERIMENTS = [e for e in MOCK_EXPERIMENTS if e["id"] != experiment_id]
