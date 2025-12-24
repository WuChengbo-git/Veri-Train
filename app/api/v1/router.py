"""
API v1 路由聚合
"""

from fastapi import APIRouter
from app.api.v1.endpoints import models, datasets, experiments

api_router = APIRouter()

# 注册各模块路由
api_router.include_router(models.router, prefix="/models", tags=["models"])
api_router.include_router(datasets.router, prefix="/datasets", tags=["datasets"])
api_router.include_router(experiments.router, prefix="/experiments", tags=["experiments"])

# TODO: 添加更多路由
# api_router.include_router(evaluation.router, prefix="/evaluation", tags=["evaluation"])
# api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
# api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
