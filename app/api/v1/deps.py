"""
API依赖注入
"""

from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.config import settings
from app.models.user import User

# HTTP Bearer认证
security = HTTPBearer()


def get_db() -> Generator:
    """
    获取数据库Session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)
) -> User:
    """
    获取当前认证用户
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="認証情報が無効です",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # 解析JWT token
        token = credentials.credentials
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # 从数据库获取用户
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(status_code=400, detail="ユーザーが無効化されています")

    return user


def get_current_active_superuser(current_user: User = Depends(get_current_user)) -> User:
    """
    获取当前管理员用户
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="管理者権限が必要です"
        )
    return current_user
