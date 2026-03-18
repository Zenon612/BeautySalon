from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.dependencies.get_db import get_db
from app.services.auth import verify_password, create_access_token, create_refresh_token
from schemas.user_schema import UserLogin
from schemas.token_schema import Token
from app.db.models.models import User

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user_data.email))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(
        user_data.password, user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data= {"sub": user.email, "user_id": user.id})
    refresh_token = create_refresh_token(data= {"sub": user.email, "user_id": user.id})

    return {"access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer"
    }