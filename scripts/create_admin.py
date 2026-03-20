from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
import argparse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import AsyncSessionLocal
from app.db.models.models import User
from app.services.auth import get_password_hash

async def create_admin(email: str, password: str, full_name: str):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
        select(User).where(User.email == email)
        )
        existing = result.scalar_one_or_none()
        if existing:
            print(f"Пользователь {email} уже существует")
            return
        admin = User(
            email=email,
            hashed_password=get_password_hash(password),
            full_name=full_name,
            is_active=True,
            is_admin=True
        )

        session.add(admin)
        await session.commit()
        print(f"Создан Администратор:")
        print(f"    email: {email}")
        print(f"    full_name: {full_name}")
        print(f"    password: {password}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Создание администратора")
    parser.add_argument("--email", required=True, help="Email админа")
    parser.add_argument("--password", required=True, help="Пароль админа")
    parser.add_argument("--name", required=True, help="Полное имя")

    args = parser.parse_args()

    if len(args.password) < 8:
        print("Пароль должен содержать минимум 8 символов!")
        exit(1)

    asyncio.run(create_admin(args.email, args.password, args.name))