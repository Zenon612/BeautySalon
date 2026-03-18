import re
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, EmailStr, field_validator


class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    phone: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Пароль должен содержать хотя-бы 8 символов')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Пароль должен содержать хотя-бы одну заглавную букву')
        if not re.search(r'[a-z]', v):
            raise ValueError('Пароль должен содержать хотя-бы одну строчную букву')
        if not re.search(r'\d', v):
            raise ValueError('Пароль должен содержать хотя-бы одну цифру')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Минимум 8 символов")

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)