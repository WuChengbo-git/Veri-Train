from pydantic import BaseModel
from typing import Optional, List, Literal, Any
from datetime import datetime


class Report(BaseModel):
    id: str
    experimentId: str
    title: str
    description: str
    type: Literal["performance", "comparison", "analysis", "summary"]
    status: Literal["draft", "published", "generating"]
    createdAt: str
    publishedAt: Optional[str] = None
    createdBy: str
    tags: Optional[List[str]] = None


class ReportImprovement(BaseModel):
    metric: str
    before: float
    after: float
    delta: float


class ReportRegression(BaseModel):
    metric: str
    before: float
    after: float
    delta: float
    reason: Optional[str] = None


class ReportSummary(BaseModel):
    changes: List[str]
    improvements: List[ReportImprovement]
    regressions: List[ReportRegression]


class ComparisonAnalysis(BaseModel):
    baselineModel: str
    targetModel: str
    datasets: List[str]
    metrics: dict[str, Any]


class SyntheticDataImpact(BaseModel):
    syntheticRatio: float
    qualityScore: float
    impact: str
    details: List[str]


class MetricsSummary(BaseModel):
    avgBleu: Optional[float] = None
    avgRougeL: Optional[float] = None
    avgRibes: Optional[float] = None
    bestModel: Optional[str] = None
    improvementRate: Optional[float] = None


class ChartData(BaseModel):
    type: Literal["line", "bar", "radar", "scatter"]
    title: str
    data: Any


class ReportDetail(Report):
    summary: ReportSummary
    comparison: ComparisonAnalysis
    syntheticDataAnalysis: SyntheticDataImpact
    metricsSummary: MetricsSummary
    charts: List[ChartData]
    conclusions: List[str]
    recommendations: List[str]
    nextSteps: List[str]


class ReportCreate(BaseModel):
    title: str
    description: str
    type: str
    experimentId: str


class ReportUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None
