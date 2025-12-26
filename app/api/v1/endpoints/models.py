"""
Models API endpoints (with mock data)
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID, uuid4
from datetime import datetime, timedelta
import random

from app.api.v1.deps import get_db
from app.schemas.model import (
    Model,
    ModelDetail,
    ModelCreate,
    RunProbeRequest,
    BaselineProbe,
    PromptContract,
)
from app.schemas.common import PaginatedResponse

router = APIRouter()

# 假数据生成器
def generate_mock_models(count: int = 12) -> list:
    """生成模拟模型数据"""
    models = []
    types = ["base", "adapter"]
    statuses = ["available", "training", "deprecated"]
    base_models = ["gpt-4o", "llama-3-70b", "qwen-2.5-72b", "gemini-pro"]

    # 生成基础模型
    for i in range(6):
        base_name = random.choice(base_models)
        model = {
            "id": str(uuid4()),
            "name": f"{base_name}-{random.randint(20230101, 20241231)}",
            "type": "base",
            "base_model_id": None,
            "status": random.choice(statuses),
            "config": {
                "max_tokens": random.choice([4096, 8192, 16384]),
                "temperature": round(random.uniform(0.5, 1.0), 2),
            },
            "metadata_": {
                "parameters": f"{random.choice([7, 13, 70])}B",
                "tokenizer": f"{base_name}-tokenizer",
                "source": random.choice(["openai", "meta", "alibaba", "google"]),
            },
            "baseline_probe": {
                "is_multi_candidate": random.choice([True, False]),
                "has_explanation": random.choice([True, False]),
                "follows_output_contract": random.choice([True, False]),
                "probed_at": (datetime.utcnow() - timedelta(days=random.randint(1, 10))).isoformat(),
                "details": {
                    "avg_response_time": round(random.uniform(0.5, 2.0), 2),
                    "success_rate": round(random.uniform(0.85, 0.99), 2),
                },
            },
            "created_at": (datetime.utcnow() - timedelta(days=random.randint(30, 90))).isoformat(),
            "updated_at": (datetime.utcnow() - timedelta(hours=random.randint(1, 24))).isoformat(),
        }
        models.append(model)

    # 生成适配器模型
    base_ids = [m["id"] for m in models[:3]]  # 取前3个基础模型
    for i in range(6):
        model = {
            "id": str(uuid4()),
            "name": f"adapter-ja-en-v{random.randint(1, 5)}-{random.choice(['meeting', 'written'])}",
            "type": "adapter",
            "base_model_id": random.choice(base_ids),
            "status": random.choice(statuses),
            "config": {
                "lora_r": random.choice([8, 16, 32]),
                "lora_alpha": random.choice([16, 32, 64]),
                "target_modules": ["q_proj", "v_proj"],
            },
            "metadata_": {
                "training_dataset": f"dataset-{random.randint(1000, 9999)}",
                "training_steps": random.randint(1000, 5000),
                "best_score": round(random.uniform(0.6, 0.85), 2),
            },
            "baseline_probe": None,  # 适配器通常不单独探测
            "created_at": (datetime.utcnow() - timedelta(days=random.randint(1, 30))).isoformat(),
            "updated_at": (datetime.utcnow() - timedelta(hours=random.randint(1, 24))).isoformat(),
        }
        models.append(model)

    return models


# 全局模拟数据
MOCK_MODELS = generate_mock_models(12)


@router.get("", response_model=PaginatedResponse[Model])
async def get_models(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    type: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    モデル一覧を取得
    """
    # 过滤
    filtered = MOCK_MODELS.copy()

    if status:
        filtered = [m for m in filtered if m["status"] == status]
    if type:
        filtered = [m for m in filtered if m["type"] == type]
    if search:
        filtered = [m for m in filtered if search.lower() in m["name"].lower()]

    # 分页
    total = len(filtered)
    start = (page - 1) * page_size
    end = start + page_size
    items = filtered[start:end]

    total_pages = (total + page_size - 1) // page_size

    return PaginatedResponse(
        items=items, total=total, page=page, page_size=page_size, total_pages=total_pages
    )


@router.get("/{model_id}", response_model=ModelDetail)
async def get_model_detail(
    model_id: str,
    db: Session = Depends(get_db),
):
    """
    モデル詳細を取得
    """
    # 查找模型
    model = next((m for m in MOCK_MODELS if m["id"] == model_id), None)
    if not model:
        raise HTTPException(status_code=404, detail="モデルが見つかりません")

    # 生成详细信息
    detail = {
        **model,
        "prompt_contracts": [
            {
                "id": str(uuid4()),
                "name": f"contract-{i+1}",
                "version": random.randint(1, 3),
                "template": f"翻訳してください: {{{{text}}}}",
                "model_id": model["id"],
                "created_at": (datetime.utcnow() - timedelta(days=random.randint(1, 20))).isoformat(),
                "updated_at": (datetime.utcnow() - timedelta(hours=random.randint(1, 12))).isoformat(),
            }
            for i in range(random.randint(1, 3))
        ],
        "evaluation_summary": {
            "total_evaluations": random.randint(5, 20),
            "avg_bleu": round(random.uniform(0.4, 0.7), 2),
            "avg_rouge_l": round(random.uniform(0.45, 0.75), 2),
            "best_experiment": {
                "id": str(uuid4()),
                "name": f"exp-{random.randint(1000, 9999)}",
                "score": round(random.uniform(0.6, 0.85), 2),
            },
        } if model["type"] == "adapter" else None,
    }

    return detail


@router.post("", response_model=Model, status_code=201)
async def create_model(
    model_data: ModelCreate,
    db: Session = Depends(get_db),
):
    """
    新規モデルを作成
    """
    new_model = {
        "id": str(uuid4()),
        "name": model_data.name,
        "type": model_data.type,
        "base_model_id": str(model_data.base_model_id) if model_data.base_model_id else None,
        "status": model_data.status,
        "config": model_data.config,
        "metadata_": model_data.metadata.dict() if model_data.metadata else None,
        "baseline_probe": None,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }

    MOCK_MODELS.insert(0, new_model)
    return new_model


@router.post("/{model_id}/probe", response_model=BaselineProbe)
async def run_baseline_probe(
    model_id: str,
    request: RunProbeRequest = RunProbeRequest(),
    db: Session = Depends(get_db),
):
    """
    ベースライン動作探査を実行

    このエンドポイントは重要な機能:
    - モデルが多候補出力をサポートするか
    - 説明性出力を提供するか
    - 出力契約に従うか
    """
    # 查找模型
    model = next((m for m in MOCK_MODELS if m["id"] == model_id), None)
    if not model:
        raise HTTPException(status_code=404, detail="モデルが見つかりません")

    # 生成探测结果
    probe_result = {
        "is_multi_candidate": random.choice([True, False]),
        "has_explanation": random.choice([True, False]),
        "follows_output_contract": random.choice([True, False]),
        "probed_at": datetime.utcnow().isoformat(),
        "details": {
            "test_cases_count": len(request.test_cases) if request.test_cases else 5,
            "avg_response_time": round(random.uniform(0.5, 2.0), 2),
            "success_rate": round(random.uniform(0.85, 0.99), 2),
            "samples": [
                {
                    "input": "こんにちは",
                    "output": "Hello",
                    "candidates": ["Hello", "Hi", "Greetings"] if random.choice([True, False]) else None,
                }
            ],
        },
    }

    # 更新模型的baseline_probe
    for m in MOCK_MODELS:
        if m["id"] == model_id:
            m["baseline_probe"] = probe_result
            break

    return probe_result


@router.get("/{model_id}/evaluations")
async def get_model_evaluations(
    model_id: str,
    db: Session = Depends(get_db),
):
    """
    モデルの評価履歴を取得
    """
    # 查找模型
    model = next((m for m in MOCK_MODELS if m["id"] == model_id), None)
    if not model:
        raise HTTPException(status_code=404, detail="モデルが見つかりません")

    # 生成评估历史
    evaluations = [
        {
            "id": str(uuid4()),
            "experiment_id": str(uuid4()),
            "experiment_name": f"exp-{random.randint(1000, 9999)}",
            "dataset_name": f"dataset-{random.randint(1000, 9999)}",
            "bleu": round(random.uniform(0.3, 0.7), 2),
            "rouge_l": round(random.uniform(0.35, 0.75), 2),
            "ribes": round(random.uniform(0.4, 0.8), 2),
            "evaluated_at": (datetime.utcnow() - timedelta(days=i)).isoformat(),
        }
        for i in range(random.randint(3, 8))
    ]

    return {"items": evaluations, "total": len(evaluations)}


@router.patch("/{model_id}/status", response_model=Model)
async def update_model_status(
    model_id: str,
    status: str = Query(..., regex="^(available|training|deprecated)$"),
    db: Session = Depends(get_db),
):
    """
    モデルステータスを更新
    """
    # 查找并更新模型
    for model in MOCK_MODELS:
        if model["id"] == model_id:
            model["status"] = status
            model["updated_at"] = datetime.utcnow().isoformat()
            return model

    raise HTTPException(status_code=404, detail="モデルが見つかりません")


@router.delete("/{model_id}", status_code=204)
async def delete_model(
    model_id: str,
    db: Session = Depends(get_db),
):
    """
    モデルを削除
    """
    global MOCK_MODELS
    MOCK_MODELS = [m for m in MOCK_MODELS if m["id"] != model_id]
