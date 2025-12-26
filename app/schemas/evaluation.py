"""
Evaluation相关Schema定义
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from app.schemas.common import BaseSchema


class GPTEval1(BaseModel):
    """GPT评价指标1 - 流畅性/适切性/正确性"""

    fluency: float  # 1-5
    adequacy: float  # 1-5
    accuracy: float  # 1-5


class GPTEval2(BaseModel):
    """GPT评价指标2 - MQM"""

    mqm_score: float  # 0-100
    error_distribution: Dict[str, int] = {}


class EvaluationMetrics(BaseModel):
    """评测指标"""

    bleu: Optional[float] = None
    rouge_l: Optional[float] = None
    ribes: Optional[float] = None
    gpt_eval_1: Optional[GPTEval1] = None
    gpt_eval_2: Optional[GPTEval2] = None


class ErrorAnalysis(BaseModel):
    """错误分析"""

    top_errors: List[Dict[str, Any]] = []
    error_type_distribution: Dict[str, int] = {}


class EvaluationBase(BaseModel):
    """Evaluation基础"""

    experiment_id: UUID
    track: str  # 'spoken' | 'written'


class EvaluationCreate(EvaluationBase):
    """创建Evaluation"""

    metrics: EvaluationMetrics
    error_analysis: Optional[ErrorAnalysis] = None


class Evaluation(EvaluationBase, BaseSchema):
    """Evaluation完整信息"""

    metrics: Dict[str, Any]
    error_analysis: Dict[str, Any] = {}


class EvaluationDetail(Evaluation):
    """Evaluation详情"""

    experiment_name: Optional[str] = None
    dataset_name: Optional[str] = None
    model_name: Optional[str] = None
    sample_results: List[Dict[str, Any]] = []  # 样本展示
