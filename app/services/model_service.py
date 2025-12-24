"""
Model Service - 模型业务逻辑层
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from uuid import UUID

from app.models.model import Model
from app.schemas.model import ModelCreate, BaselineProbe
from app.schemas.common import PaginatedResponse
import structlog

logger = structlog.get_logger()


class ModelService:
    """模型服务类"""

    def __init__(self, db: Session):
        self.db = db

    def get_models(
        self,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
        model_type: Optional[str] = None,
    ) -> PaginatedResponse:
        """获取模型列表(分页)"""

        query = self.db.query(Model)

        # 过滤条件
        if status:
            query = query.filter(Model.status == status)
        if model_type:
            query = query.filter(Model.type == model_type)

        # 总数
        total = query.count()

        # 分页
        offset = (page - 1) * page_size
        models = query.offset(offset).limit(page_size).all()

        total_pages = (total + page_size - 1) // page_size

        return PaginatedResponse(
            items=models, total=total, page=page, page_size=page_size, total_pages=total_pages
        )

    def get_model_by_id(self, model_id: UUID) -> Optional[Model]:
        """根据ID获取模型"""
        return self.db.query(Model).filter(Model.id == model_id).first()

    def create_model(self, model_data: ModelCreate) -> Model:
        """创建新模型"""

        db_model = Model(
            name=model_data.name,
            type=model_data.type,
            base_model_id=model_data.base_model_id,
            status=model_data.status,
            config=model_data.config,
            metadata_=model_data.metadata.dict() if model_data.metadata else {},
        )

        self.db.add(db_model)
        self.db.commit()
        self.db.refresh(db_model)

        logger.info("model_created", model_id=str(db_model.id), name=db_model.name)

        return db_model

    def run_baseline_probe(
        self, model_id: UUID, test_cases: Optional[List[Dict[str, Any]]] = None
    ) -> BaselineProbe:
        """
        运行基线行为探测

        这是系统的核心创新功能!
        检测模型的基础能力:
        1. 是否支持多候选输出
        2. 是否提供解释性输出
        3. 是否遵循输出契约
        """

        model = self.get_model_by_id(model_id)
        if not model:
            raise ValueError("モデルが見つかりません")

        # TODO: 实际的探测逻辑
        # 1. 加载模型
        # 2. 运行测试用例
        # 3. 分析输出

        # 示例实现(需要实际的模型推理逻辑)
        probe_result = BaselineProbe(
            is_multi_candidate=True,  # 示例值
            has_explanation=False,
            follows_output_contract=True,
            probed_at=datetime.utcnow(),
            details={
                "test_count": len(test_cases) if test_cases else 0,
                "notes": "Baseline probe completed",
            },
        )

        # 保存探测结果到数据库
        model.baseline_probe = probe_result.dict()
        self.db.commit()

        logger.info(
            "baseline_probe_completed",
            model_id=str(model_id),
            result=probe_result.dict(),
        )

        return probe_result

    def get_model_evaluations(self, model_id: UUID) -> List[Dict]:
        """获取模型的评测历史"""
        # TODO: 从Evaluation表查询
        return []

    def update_model_status(self, model_id: UUID, status: str) -> Optional[Model]:
        """更新模型状态"""
        model = self.get_model_by_id(model_id)
        if not model:
            return None

        model.status = status
        self.db.commit()
        self.db.refresh(model)

        logger.info("model_status_updated", model_id=str(model_id), status=status)

        return model

    def delete_model(self, model_id: UUID) -> bool:
        """删除模型"""
        model = self.get_model_by_id(model_id)
        if not model:
            return False

        self.db.delete(model)
        self.db.commit()

        logger.info("model_deleted", model_id=str(model_id))

        return True
