"""
Settings API endpoints (with mock data)
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import time
import random

from app.api.v1.deps import get_db
from app.schemas.settings import (
    SystemSettings,
    UserPreferences,
    SystemSettingsUpdate,
    UserPreferencesUpdate,
    ConnectionTestRequest,
    ConnectionTestResponse,
    CleanupStorageResponse,
    GeneralSettings,
    TrainingSettings,
    EvaluationSettings,
    StorageSettings,
    ApiSettings,
    SecuritySettings,
)

router = APIRouter()


# Mock 系统设置数据
MOCK_SYSTEM_SETTINGS = {
    "general": {
        "language": "ja",
        "timezone": "Asia/Tokyo",
        "theme": "light",
        "notifications_enabled": True,
    },
    "training": {
        "default_epochs": 10,
        "default_batch_size": 32,
        "default_learning_rate": 0.0001,
        "auto_save_checkpoints": True,
        "checkpoint_interval": 5,
        "early_stopping_enabled": True,
        "early_stopping_patience": 3,
    },
    "evaluation": {
        "default_metrics": ["BLEU", "ROUGE-L", "RIBES"],
        "enable_gpt_eval": True,
        "gpt_model": "gpt-4o",
        "enable_human_eval": False,
        "confidence_threshold": 0.85,
    },
    "storage": {
        "data_retention_days": 90,
        "auto_cleanup_enabled": True,
        "max_storage_gb": 1000,
        "current_usage_gb": 342.5,
    },
    "api": {
        "base_url": "http://localhost:8000/api/v1",
        "timeout_seconds": 30,
        "retry_attempts": 3,
        "rate_limit_per_minute": 60,
    },
    "security": {
        "two_factor_enabled": False,
        "session_timeout_minutes": 120,
        "password_expiry_days": 90,
        "ip_whitelist": ["127.0.0.1", "10.0.0.0/8"],
    },
}


# Mock 用户偏好设置数据
MOCK_USER_PREFERENCES = {
    "user_id": "user_12345",
    "email": "user@example.com",
    "display_name": "山田太郎",
    "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=user12345",
    "email_notifications": True,
    "desktop_notifications": True,
    "weekly_summary": True,
    "preferred_language": "ja",
    "items_per_page": 20,
    "default_view": "table",
}


@router.get("/system", response_model=SystemSettings)
async def get_system_settings(
    db: Session = Depends(get_db),
):
    """
    获取系统设置
    """
    return MOCK_SYSTEM_SETTINGS


@router.put("/system", response_model=SystemSettings)
async def update_system_settings(
    data: SystemSettingsUpdate,
    db: Session = Depends(get_db),
):
    """
    更新系统设置
    """
    # 更新设置
    if data.general is not None:
        MOCK_SYSTEM_SETTINGS["general"] = data.general.dict()
    if data.training is not None:
        MOCK_SYSTEM_SETTINGS["training"] = data.training.dict()
    if data.evaluation is not None:
        MOCK_SYSTEM_SETTINGS["evaluation"] = data.evaluation.dict()
    if data.storage is not None:
        MOCK_SYSTEM_SETTINGS["storage"] = data.storage.dict()
    if data.api is not None:
        MOCK_SYSTEM_SETTINGS["api"] = data.api.dict()
    if data.security is not None:
        MOCK_SYSTEM_SETTINGS["security"] = data.security.dict()

    return MOCK_SYSTEM_SETTINGS


@router.get("/preferences", response_model=UserPreferences)
async def get_user_preferences(
    db: Session = Depends(get_db),
):
    """
    获取用户偏好设置
    """
    return MOCK_USER_PREFERENCES


@router.put("/preferences", response_model=UserPreferences)
async def update_user_preferences(
    data: UserPreferencesUpdate,
    db: Session = Depends(get_db),
):
    """
    更新用户偏好设置
    """
    # 更新设置
    if data.display_name is not None:
        MOCK_USER_PREFERENCES["display_name"] = data.display_name
    if data.avatar_url is not None:
        MOCK_USER_PREFERENCES["avatar_url"] = data.avatar_url
    if data.email_notifications is not None:
        MOCK_USER_PREFERENCES["email_notifications"] = data.email_notifications
    if data.desktop_notifications is not None:
        MOCK_USER_PREFERENCES["desktop_notifications"] = data.desktop_notifications
    if data.weekly_summary is not None:
        MOCK_USER_PREFERENCES["weekly_summary"] = data.weekly_summary
    if data.preferred_language is not None:
        MOCK_USER_PREFERENCES["preferred_language"] = data.preferred_language
    if data.items_per_page is not None:
        MOCK_USER_PREFERENCES["items_per_page"] = data.items_per_page
    if data.default_view is not None:
        MOCK_USER_PREFERENCES["default_view"] = data.default_view

    return MOCK_USER_PREFERENCES


@router.post("/system/reset", response_model=SystemSettings)
async def reset_system_settings(
    db: Session = Depends(get_db),
):
    """
    重置系统设置为默认值
    """
    # 重置为默认值
    MOCK_SYSTEM_SETTINGS.update({
        "general": {
            "language": "ja",
            "timezone": "Asia/Tokyo",
            "theme": "light",
            "notifications_enabled": True,
        },
        "training": {
            "default_epochs": 10,
            "default_batch_size": 32,
            "default_learning_rate": 0.0001,
            "auto_save_checkpoints": True,
            "checkpoint_interval": 5,
            "early_stopping_enabled": True,
            "early_stopping_patience": 3,
        },
        "evaluation": {
            "default_metrics": ["BLEU", "ROUGE-L", "RIBES"],
            "enable_gpt_eval": True,
            "gpt_model": "gpt-4o",
            "enable_human_eval": False,
            "confidence_threshold": 0.85,
        },
        "storage": {
            "data_retention_days": 90,
            "auto_cleanup_enabled": True,
            "max_storage_gb": 1000,
            "current_usage_gb": 342.5,
        },
        "api": {
            "base_url": "http://localhost:8000/api/v1",
            "timeout_seconds": 30,
            "retry_attempts": 3,
            "rate_limit_per_minute": 60,
        },
        "security": {
            "two_factor_enabled": False,
            "session_timeout_minutes": 120,
            "password_expiry_days": 90,
            "ip_whitelist": ["127.0.0.1", "10.0.0.0/8"],
        },
    })

    return MOCK_SYSTEM_SETTINGS


@router.post("/test-connection", response_model=ConnectionTestResponse)
async def test_api_connection(
    data: ConnectionTestRequest,
    db: Session = Depends(get_db),
):
    """
    测试 API 连接
    """
    # 模拟连接测试
    start_time = time.time()

    # 模拟延迟
    time.sleep(random.uniform(0.01, 0.1))

    latency = (time.time() - start_time) * 1000  # 转换为毫秒

    # 80% 的概率成功
    success = random.random() < 0.8

    return {
        "success": success,
        "latency": round(latency, 2),
    }


@router.post("/cleanup-storage", response_model=CleanupStorageResponse)
async def cleanup_storage(
    db: Session = Depends(get_db),
):
    """
    清理存储空间
    """
    # 模拟清理操作
    deleted_items = random.randint(50, 500)
    freed_space = round(random.uniform(5.0, 50.0), 2)

    # 更新存储使用量
    MOCK_SYSTEM_SETTINGS["storage"]["current_usage_gb"] = round(
        MOCK_SYSTEM_SETTINGS["storage"]["current_usage_gb"] - freed_space, 2
    )

    return {
        "deletedItems": deleted_items,
        "freedSpace": freed_space,
    }
