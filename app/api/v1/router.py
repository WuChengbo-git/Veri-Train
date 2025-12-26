"""
API v1 路由聚合
"""

from fastapi import APIRouter
from app.api.v1.endpoints import models, datasets, experiments, evaluations, reports, settings

api_router = APIRouter()

# 注册各模块路由
api_router.include_router(models.router, prefix="/models", tags=["models"])
api_router.include_router(datasets.router, prefix="/datasets", tags=["datasets"])
api_router.include_router(experiments.router, prefix="/experiments", tags=["experiments"])
api_router.include_router(evaluations.router, prefix="/evaluations", tags=["evaluations"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])

# TODO: 添加更多路由
# api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
