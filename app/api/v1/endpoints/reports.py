"""
Reports API endpoints (with mock data)
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime, timedelta
import random

from app.api.v1.deps import get_db
from app.schemas.report import (
    Report,
    ReportDetail,
    ReportCreate,
    ReportUpdate,
    ReportSummary,
    ReportImprovement,
    ReportRegression,
    ComparisonAnalysis,
    SyntheticDataImpact,
    MetricsSummary,
    ChartData,
)
from app.schemas.common import PaginatedResponse

router = APIRouter()


# 假数据生成器
def generate_mock_reports(count: int = 15) -> list:
    """生成模拟报告数据"""
    reports = []
    types = ["performance", "comparison", "analysis", "summary"]
    statuses = ["draft", "published", "generating"]
    titles_template = {
        "performance": ["性能评估报告", "模型性能分析", "训练效果报告"],
        "comparison": ["模型对比报告", "A/B测试结果", "基准对比分析"],
        "analysis": ["错误分析报告", "数据质量分析", "综合评估报告"],
        "summary": ["实验总结报告", "月度汇总", "项目进展报告"],
    }

    for i in range(count):
        report_type = random.choice(types)
        status = random.choice(statuses)
        created_at = datetime.now() - timedelta(days=random.randint(1, 90))
        published_at = None
        if status == "published":
            published_at = (created_at + timedelta(days=random.randint(1, 7))).isoformat()

        report = {
            "id": str(uuid4()),
            "experimentId": str(uuid4()),
            "title": random.choice(titles_template[report_type]) + f" #{i+1}",
            "description": f"这是一份{report_type}类型的报告，包含详细的分析和建议。",
            "type": report_type,
            "status": status,
            "createdAt": created_at.isoformat(),
            "publishedAt": published_at,
            "createdBy": random.choice(["张三", "李四", "王五", "赵六"]),
            "tags": random.sample(
                ["ja-en", "spoken", "written", "high-priority", "baseline", "production"],
                k=random.randint(1, 3),
            ),
        }
        reports.append(report)

    # 按创建时间降序排序
    reports.sort(key=lambda x: x["createdAt"], reverse=True)
    return reports


def generate_mock_report_detail(report_id: str) -> dict:
    """生成模拟报告详情"""
    # 先生成基础报告
    base_report = generate_mock_reports(1)[0]
    base_report["id"] = report_id

    # 添加详细信息
    detail = {
        **base_report,
        "summary": {
            "changes": [
                "更新了数据集配置",
                "调整了学习率参数",
                "增加了early stopping机制",
            ],
            "improvements": [
                {
                    "metric": "BLEU",
                    "before": 24.5,
                    "after": 28.3,
                    "delta": 3.8,
                },
                {
                    "metric": "ROUGE-L",
                    "before": 0.512,
                    "after": 0.567,
                    "delta": 0.055,
                },
            ],
            "regressions": [
                {
                    "metric": "训练时间",
                    "before": 120.0,
                    "after": 145.0,
                    "delta": 25.0,
                    "reason": "增加了数据集大小",
                },
            ],
        },
        "comparison": {
            "baselineModel": "gpt-4o-baseline",
            "targetModel": "gpt-4o-finetuned",
            "datasets": ["meeting-ja-en", "written-ja-en", "mixed-data"],
            "metrics": {
                "BLEU": {"baseline": 24.5, "target": 28.3, "improvement": "15.5%"},
                "ROUGE-L": {"baseline": 0.512, "target": 0.567, "improvement": "10.7%"},
                "RIBES": {"baseline": 0.755, "target": 0.801, "improvement": "6.1%"},
            },
        },
        "syntheticDataAnalysis": {
            "syntheticRatio": 0.35,
            "qualityScore": 0.87,
            "impact": "positive",
            "details": [
                "合成数据占比35%，质量评分0.87",
                "在spoken场景下提升显著",
                "建议继续扩大合成数据比例至50%",
            ],
        },
        "metricsSummary": {
            "avgBleu": 28.3,
            "avgRougeL": 0.567,
            "avgRibes": 0.801,
            "bestModel": "gpt-4o-finetuned-v3",
            "improvementRate": 12.5,
        },
        "charts": [
            {
                "type": "line",
                "title": "训练损失曲线",
                "data": {
                    "labels": ["Epoch 1", "Epoch 2", "Epoch 3", "Epoch 4", "Epoch 5"],
                    "datasets": [
                        {
                            "label": "Training Loss",
                            "data": [2.5, 1.8, 1.3, 1.0, 0.8],
                        },
                        {
                            "label": "Validation Loss",
                            "data": [2.3, 1.7, 1.4, 1.2, 1.1],
                        },
                    ],
                },
            },
            {
                "type": "bar",
                "title": "指标对比",
                "data": {
                    "labels": ["BLEU", "ROUGE-L", "RIBES"],
                    "datasets": [
                        {
                            "label": "Baseline",
                            "data": [24.5, 51.2, 75.5],
                        },
                        {
                            "label": "Fine-tuned",
                            "data": [28.3, 56.7, 80.1],
                        },
                    ],
                },
            },
        ],
        "conclusions": [
            "模型在所有主要指标上都有显著提升",
            "合成数据的引入对spoken场景效果明显",
            "early stopping有效防止了过拟合",
        ],
        "recommendations": [
            "建议将该模型部署到生产环境",
            "继续扩大合成数据的比例",
            "对written场景进行针对性优化",
        ],
        "nextSteps": [
            "在更大的测试集上进行验证",
            "进行A/B测试评估实际效果",
            "收集用户反馈并迭代改进",
        ],
    }

    return detail


# Mock数据存储
MOCK_REPORTS = generate_mock_reports(15)


@router.get("", response_model=PaginatedResponse[Report])
async def get_reports(
    page: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1, le=100),
    type: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    获取报告列表（支持分页和过滤）
    """
    # 过滤
    filtered_reports = MOCK_REPORTS

    if type:
        filtered_reports = [r for r in filtered_reports if r["type"] == type]

    if status:
        filtered_reports = [r for r in filtered_reports if r["status"] == status]

    if search:
        search_lower = search.lower()
        filtered_reports = [
            r
            for r in filtered_reports
            if search_lower in r["title"].lower()
            or search_lower in r["description"].lower()
        ]

    # 分页
    total = len(filtered_reports)
    start = (page - 1) * pageSize
    end = start + pageSize
    items = filtered_reports[start:end]

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": pageSize,
        "total_pages": (total + pageSize - 1) // pageSize,
    }


@router.get("/{report_id}", response_model=ReportDetail)
async def get_report_detail(
    report_id: str,
    db: Session = Depends(get_db),
):
    """
    获取报告详情
    """
    # 检查报告是否存在
    report = next((r for r in MOCK_REPORTS if r["id"] == report_id), None)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    return generate_mock_report_detail(report_id)


@router.post("", response_model=Report)
async def create_report(
    data: ReportCreate,
    db: Session = Depends(get_db),
):
    """
    创建新报告
    """
    new_report = {
        "id": str(uuid4()),
        "experimentId": data.experimentId,
        "title": data.title,
        "description": data.description,
        "type": data.type,
        "status": "draft",
        "createdAt": datetime.now().isoformat(),
        "publishedAt": None,
        "createdBy": "当前用户",
        "tags": [],
    }

    MOCK_REPORTS.insert(0, new_report)
    return new_report


@router.put("/{report_id}", response_model=Report)
async def update_report(
    report_id: str,
    data: ReportUpdate,
    db: Session = Depends(get_db),
):
    """
    更新报告
    """
    report = next((r for r in MOCK_REPORTS if r["id"] == report_id), None)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    # 更新字段
    if data.title is not None:
        report["title"] = data.title
    if data.description is not None:
        report["description"] = data.description
    if data.type is not None:
        report["type"] = data.type
    if data.status is not None:
        report["status"] = data.status
    if data.tags is not None:
        report["tags"] = data.tags

    return report


@router.delete("/{report_id}")
async def delete_report(
    report_id: str,
    db: Session = Depends(get_db),
):
    """
    删除报告
    """
    global MOCK_REPORTS
    report = next((r for r in MOCK_REPORTS if r["id"] == report_id), None)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    MOCK_REPORTS = [r for r in MOCK_REPORTS if r["id"] != report_id]
    return {"message": "Report deleted successfully"}


@router.post("/{report_id}/publish", response_model=Report)
async def publish_report(
    report_id: str,
    db: Session = Depends(get_db),
):
    """
    发布报告
    """
    report = next((r for r in MOCK_REPORTS if r["id"] == report_id), None)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    report["status"] = "published"
    report["publishedAt"] = datetime.now().isoformat()

    return report


@router.get("/{report_id}/export")
async def export_report(
    report_id: str,
    format: str = Query("pdf", regex="^(pdf|docx|html)$"),
    db: Session = Depends(get_db),
):
    """
    导出报告（模拟）
    """
    report = next((r for r in MOCK_REPORTS if r["id"] == report_id), None)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    # 模拟导出
    return {
        "message": f"Report exported as {format}",
        "downloadUrl": f"/downloads/reports/{report_id}.{format}",
    }
