from pydantic import BaseModel
from typing import Optional, List, Literal


class GeneralSettings(BaseModel):
    language: Literal["ja", "en", "zh"]
    timezone: str
    theme: Literal["light", "dark", "auto"]
    notifications_enabled: bool


class TrainingSettings(BaseModel):
    default_epochs: int
    default_batch_size: int
    default_learning_rate: float
    auto_save_checkpoints: bool
    checkpoint_interval: int
    early_stopping_enabled: bool
    early_stopping_patience: int


class EvaluationSettings(BaseModel):
    default_metrics: List[str]
    enable_gpt_eval: bool
    gpt_model: str
    enable_human_eval: bool
    confidence_threshold: float


class StorageSettings(BaseModel):
    data_retention_days: int
    auto_cleanup_enabled: bool
    max_storage_gb: int
    current_usage_gb: float


class ApiSettings(BaseModel):
    base_url: str
    timeout_seconds: int
    retry_attempts: int
    rate_limit_per_minute: int


class SecuritySettings(BaseModel):
    two_factor_enabled: bool
    session_timeout_minutes: int
    password_expiry_days: int
    ip_whitelist: List[str]


class SystemSettings(BaseModel):
    general: GeneralSettings
    training: TrainingSettings
    evaluation: EvaluationSettings
    storage: StorageSettings
    api: ApiSettings
    security: SecuritySettings


class UserPreferences(BaseModel):
    user_id: str
    email: str
    display_name: str
    avatar_url: Optional[str] = None
    email_notifications: bool
    desktop_notifications: bool
    weekly_summary: bool
    preferred_language: Literal["ja", "en", "zh"]
    items_per_page: int
    default_view: Literal["table", "grid"]


class SystemSettingsUpdate(BaseModel):
    general: Optional[GeneralSettings] = None
    training: Optional[TrainingSettings] = None
    evaluation: Optional[EvaluationSettings] = None
    storage: Optional[StorageSettings] = None
    api: Optional[ApiSettings] = None
    security: Optional[SecuritySettings] = None


class UserPreferencesUpdate(BaseModel):
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    email_notifications: Optional[bool] = None
    desktop_notifications: Optional[bool] = None
    weekly_summary: Optional[bool] = None
    preferred_language: Optional[Literal["ja", "en", "zh"]] = None
    items_per_page: Optional[int] = None
    default_view: Optional[Literal["table", "grid"]] = None


class ConnectionTestRequest(BaseModel):
    url: str


class ConnectionTestResponse(BaseModel):
    success: bool
    latency: float


class CleanupStorageResponse(BaseModel):
    deletedItems: int
    freedSpace: float
