"""
Dataset相关Schema定义
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from uuid import UUID
from app.schemas.common import BaseSchema


class DatasetOverview(BaseModel):
    """数据集概览"""

    total_count: int
    avg_sentence_length: float
    short_sentence_ratio: float
    code_switch_ratio: float = 0.0


class QualityGateMetrics(BaseModel):
    """质量门禁指标"""

    alignment_rate: float
    duplicate_rate: float
    language_consistency: float


class SamplingReview(BaseModel):
    """抽样审阅"""

    reviewed_by: str
    reviewed_at: str
    sample_size: int
    pass_rate: float
    comments: str


class QualityGateResult(BaseModel):
    """质量门禁结果"""

    status: str  # 'passed' | 'failed' | 'pending'
    checked_at: Optional[str] = None
    metrics: QualityGateMetrics
    sampling_review: Optional[SamplingReview] = None
    block_reasons: Optional[List[str]] = None


class DatasetBase(BaseModel):
    """Dataset基础"""

    name: str
    type: str  # 'human' | 'synthetic' | 'mixed'
    language_direction: str  # 'ja-en' | 'en-ja'
    scene: str  # 'meeting' | 'written'
    version: int = 1


class DatasetCreate(DatasetBase):
    """创建Dataset"""

    parent_id: Optional[UUID] = None


class Dataset(DatasetBase, BaseSchema):
    """Dataset完整信息"""

    status: str = "draft"  # 'draft' | 'passed' | 'blocked'
    parent_id: Optional[UUID] = None
    file_path: Optional[str] = None


class DatasetDetail(Dataset):
    """Dataset详情"""

    overview: Optional[DatasetOverview] = None
    quality_gate_result: Optional[QualityGateResult] = None
    usage_history: List[Dict[str, Any]] = []


class GenerateDatasetConfig(BaseModel):
    """生成数据集配置"""

    task: str = "translation"
    direction: str
    scene: str
    seed_source: Dict[str, Any]
    strategy: Dict[str, Any]
    target_count: int


class GenerateEstimate(BaseModel):
    """生成估算"""

    total_tokens: int
    estimated_cost: float
    estimated_time: str
