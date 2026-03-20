from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.db.models.models import User
from app.api.v1.dependencies.get_db import get_db
from sqlalchemy import select
from typing import Optional


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db)) -> User:
    """
    Декодирует JWT токен и возвращает пользователя из БД.
    :param token:
    :param db:
    :return: User
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось проверить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
        token,
        settings.secret_key,
        algorithms=[settings.algorithm])

        email: Optional[str] = payload.get("sub")
        user_id: Optional[int] = payload.get("user_id")

        if email is None or user_id is None:
            raise credentials_exception

        token_type: Optional[str] = payload.get("type")

        if token_type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Требуется access token",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise credentials_exception
    result = await db.execute(
        select(User).where(User.email == email, User.id == user_id)
    )

    user = result.scalar_one_or_none()

    if user is None or not user.is_active:
        raise credentials_exception

    return user

async def get_current_active_admin(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Требуются права администратора")
    return current_user