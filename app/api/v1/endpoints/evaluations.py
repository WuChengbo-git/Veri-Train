"""
Evaluations API endpoints (with mock data)
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID, uuid4
from datetime import datetime, timedelta
import random

from app.api.v1.deps import get_db
from app.schemas.evaluation import (
    Evaluation,
    EvaluationDetail,
    EvaluationCreate,
)
from app.schemas.common import PaginatedResponse

router = APIRouter()


# 假数据生成器
def generate_mock_evaluations(count: int = 20) -> list:
    """生成模拟评测数据"""
    evaluations = []
    tracks = ["spoken", "written"]

    for i in range(count):
        track = random.choice(tracks)

        # 不同track的指标范围略有不同
        if track == "spoken":
            bleu_range = (0.3, 0.6)
            rouge_range = (0.35, 0.65)
            ribes_range = (0.5, 0.8)
        else:
            bleu_range = (0.4, 0.75)
            rouge_range = (0.45, 0.8)
            ribes_range = (0.55, 0.85)

        evaluation = {
            "id": str(uuid4()),
            "experiment_id": str(uuid4()),
            "track": track,
            "metrics": {
                "bleu": round(random.uniform(*bleu_range), 2),
                "rouge_l": round(random.uniform(*rouge_range), 2),
                "ribes": round(random.uniform(*ribes_range), 2),
                "gpt_eval_1": {
                    "fluency": round(random.uniform(3.0, 5.0), 1),
                    "adequacy": round(random.uniform(3.0, 5.0), 1),
                    "accuracy": round(random.uniform(3.0, 5.0), 1),
                },
                "gpt_eval_2": {
                    "mqm_score": round(random.uniform(70.0, 95.0), 1),
                    "error_distribution": {
                        "minor": random.randint(5, 15),
                        "major": random.randint(1, 8),
                        "critical": random.randint(0, 3),
                    },
                },
            },
            "error_analysis": {
                "top_errors": [
                    {
                        "type": random.choice(
                            ["語彙選択", "文法", "敬語", "文脈理解", "専門用語"]
                        ),
                        "count": random.randint(3, 20),
                        "severity": random.choice(["minor", "major", "critical"]),
                    }
                    for _ in range(random.randint(3, 6))
                ],
                "error_type_distribution": {
                    "語彙選択": random.randint(5, 15),
                    "文法": random.randint(3, 10),
                    "敬語": random.randint(2, 8),
                    "文脈理解": random.randint(1, 5),
                    "専門用語": random.randint(1, 5),
                },
            },
            "created_at": (
                datetime.utcnow() - timedelta(days=random.randint(1, 30))
            ).isoformat(),
            "updated_at": (
                datetime.utcnow() - timedelta(hours=random.randint(1, 24))
            ).isoformat(),
        }
        evaluations.append(evaluation)

    return evaluations


# 全局模拟数据
MOCK_EVALUATIONS = generate_mock_evaluations(20)


@router.get("", response_model=PaginatedResponse[Evaluation])
async def get_evaluations(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    track: Optional[str] = None,
    experiment_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    評価結果一覧を取得
    """
    # 过滤
    filtered = MOCK_EVALUATIONS.copy()

    if track:
        filtered = [e for e in filtered if e["track"] == track]
    if experiment_id:
        filtered = [e for e in filtered if e["experiment_id"] == experiment_id]

    # 分页
    total = len(filtered)
    start = (page - 1) * page_size
    end = start + page_size
    items = filtered[start:end]

    total_pages = (total + page_size - 1) // page_size

    return PaginatedResponse(
        items=items, total=total, page=page, page_size=page_size, total_pages=total_pages
    )


@router.get("/{evaluation_id}", response_model=EvaluationDetail)
async def get_evaluation_detail(
    evaluation_id: str,
    db: Session = Depends(get_db),
):
    """
    評価結果詳細を取得
    """
    # 查找评测
    evaluation = next((e for e in MOCK_EVALUATIONS if e["id"] == evaluation_id), None)
    if not evaluation:
        raise HTTPException(status_code=404, detail="評価結果が見つかりません")

    # 生成详细信息
    detail = {
        **evaluation,
        "experiment_name": f"exp-{random.randint(1000, 9999)}",
        "dataset_name": f"dataset-{random.choice(['ja-en', 'en-ja'])}-{random.choice(['meeting', 'written'])}-v{random.randint(1, 5)}",
        "model_name": f"adapter-{random.choice(['ja-en', 'en-ja'])}-v{random.randint(1, 5)}",
        "sample_results": [
            {
                "source": "本日はお忙しい中お越しいただきありがとうございます。",
                "reference": "Thank you for coming today despite your busy schedule.",
                "hypothesis": "Thank you for taking the time to visit us today.",
                "scores": {
                    "bleu": round(random.uniform(0.3, 0.8), 2),
                    "rouge_l": round(random.uniform(0.4, 0.85), 2),
                },
                "errors": [
                    {
                        "type": "語彙選択",
                        "severity": "minor",
                        "description": "「お越しいただき」→「visit us」より「come」の方が自然",
                    }
                ],
            },
            {
                "source": "プロジェクトの進捗状況について報告いたします。",
                "reference": "I will report on the project progress.",
                "hypothesis": "I will report about the project status.",
                "scores": {
                    "bleu": round(random.uniform(0.3, 0.8), 2),
                    "rouge_l": round(random.uniform(0.4, 0.85), 2),
                },
                "errors": [],
            },
            {
                "source": "次回のミーティングは来週の金曜日を予定しております。",
                "reference": "The next meeting is scheduled for next Friday.",
                "hypothesis": "We plan the next meeting for Friday next week.",
                "scores": {
                    "bleu": round(random.uniform(0.3, 0.8), 2),
                    "rouge_l": round(random.uniform(0.4, 0.85), 2),
                },
                "errors": [
                    {
                        "type": "文法",
                        "severity": "minor",
                        "description": "語順が不自然「Friday next week」→「next Friday」",
                    }
                ],
            },
        ],
    }

    return detail


@router.post("", response_model=Evaluation, status_code=201)
async def create_evaluation(
    evaluation_data: EvaluationCreate,
    db: Session = Depends(get_db),
):
    """
    評価結果を作成
    """
    new_evaluation = {
        "id": str(uuid4()),
        "experiment_id": str(evaluation_data.experiment_id),
        "track": evaluation_data.track,
        "metrics": evaluation_data.metrics.dict() if evaluation_data.metrics else {},
        "error_analysis": (
            evaluation_data.error_analysis.dict()
            if evaluation_data.error_analysis
            else {}
        ),
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }

    MOCK_EVALUATIONS.insert(0, new_evaluation)
    return new_evaluation


@router.get("/experiment/{experiment_id}/summary")
async def get_experiment_evaluation_summary(
    experiment_id: str,
    db: Session = Depends(get_db),
):
    """
    実験の評価サマリーを取得 (Spoken/Written両方)
    """
    # 找到该实验的所有评测
    experiment_evals = [
        e for e in MOCK_EVALUATIONS if e["experiment_id"] == experiment_id
    ]

    if not experiment_evals:
        # 生成假数据
        spoken_eval = {
            "track": "spoken",
            "metrics": {
                "bleu": round(random.uniform(0.3, 0.6), 2),
                "rouge_l": round(random.uniform(0.35, 0.65), 2),
                "ribes": round(random.uniform(0.5, 0.8), 2),
                "gpt_eval_1": {
                    "fluency": round(random.uniform(3.0, 5.0), 1),
                    "adequacy": round(random.uniform(3.0, 5.0), 1),
                    "accuracy": round(random.uniform(3.0, 5.0), 1),
                },
            },
        }
        written_eval = {
            "track": "written",
            "metrics": {
                "bleu": round(random.uniform(0.4, 0.75), 2),
                "rouge_l": round(random.uniform(0.45, 0.8), 2),
                "ribes": round(random.uniform(0.55, 0.85), 2),
                "gpt_eval_1": {
                    "fluency": round(random.uniform(3.5, 5.0), 1),
                    "adequacy": round(random.uniform(3.5, 5.0), 1),
                    "accuracy": round(random.uniform(3.5, 5.0), 1),
                },
            },
        }
        experiment_evals = [spoken_eval, written_eval]

    # 按track分组
    spoken = next((e for e in experiment_evals if e["track"] == "spoken"), None)
    written = next((e for e in experiment_evals if e["track"] == "written"), None)

    return {
        "experiment_id": experiment_id,
        "spoken": spoken,
        "written": written,
        "comparison": {
            "better_track": (
                "spoken"
                if spoken
                and written
                and spoken["metrics"]["bleu"] > written["metrics"]["bleu"]
                else "written"
            ),
            "bleu_diff": (
                round(spoken["metrics"]["bleu"] - written["metrics"]["bleu"], 2)
                if spoken and written
                else 0.0
            ),
        },
    }


@router.delete("/{evaluation_id}", status_code=204)
async def delete_evaluation(
    evaluation_id: str,
    db: Session = Depends(get_db),
):
    """
    評価結果を削除
    """
    global MOCK_EVALUATIONS
    MOCK_EVALUATIONS = [e for e in MOCK_EVALUATIONS if e["id"] != evaluation_id]
