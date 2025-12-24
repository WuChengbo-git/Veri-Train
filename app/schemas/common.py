"""
通用Schema定义
"""

from typing import Generic, TypeVar, List
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID


class APIResponse(BaseModel):
    """API统一响应格式"""

    code: int = 200
    message: str = "success"
    data: dict | list | None = None


T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应"""

    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int


class BaseSchema(BaseModel):
    """基础Schema"""

    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskResponse(BaseModel):
    """异步任务响应"""

    task_id: str
    status: str = "started"
    message: str = "タスクが開始されました"
