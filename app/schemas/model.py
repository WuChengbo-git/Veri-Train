"""
Model相关Schema定义
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from app.schemas.common import BaseSchema


class BaselineProbe(BaseModel):
    """基线行为探测结果"""

    is_multi_candidate: bool
    has_explanation: bool
    follows_output_contract: bool
    probed_at: datetime
    details: Dict[str, Any] = {}


class PromptContractBase(BaseModel):
    """Prompt Contract基础"""

    name: str
    version: int = 1
    template: str


class PromptContract(PromptContractBase, BaseSchema):
    """Prompt Contract"""

    model_id: UUID


class ModelMetadata(BaseModel):
    """模型元数据"""

    parameters: Optional[str] = None
    tokenizer: Optional[str] = None
    source: Optional[str] = None


class ModelBase(BaseModel):
    """Model基础"""

    name: str
    type: str  # 'base' | 'adapter'
    base_model_id: Optional[UUID] = None
    status: str = "available"
    config: Dict[str, Any] = {}


class ModelCreate(ModelBase):
    """创建Model"""

    metadata: Optional[ModelMetadata] = None


class Model(ModelBase, BaseSchema):
    """Model完整信息"""

    metadata_: Optional[Dict[str, Any]] = None
    baseline_probe: Optional[BaselineProbe] = None


class ModelDetail(Model):
    """Model详情"""

    prompt_contracts: List[PromptContract] = []
    evaluation_summary: Optional[Dict[str, Any]] = None


class RunProbeRequest(BaseModel):
    """运行探测请求"""

    test_cases: Optional[List[Dict[str, Any]]] = None
