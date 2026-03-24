"""
Скрипт для наполнения базы данных тестовыми данными.
Запуск: python scripts/seed_data.py
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.db.models.models import (
    Service, ServiceCategory, Master, PortfolioItem, ContactInfo
)
from app.core.config import settings


async def seed_data():
    engine = create_async_engine(settings.database_url, echo=False)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionLocal() as db:
        print("Начинаем наполнение базы данными")

        # === Услуги ===
        services_data = [
            {
                "name": "Стрижка женская",
                "description": "Профессиональная стрижка с укладкой",
                "category": ServiceCategory.HAIR,
                "price": 2500,
                "duration_minutes": 60,
            },
            {
                "name": "Стрижка мужская",
                "description": "Классическая стрижка",
                "category": ServiceCategory.HAIR,
                "price": 1800,
                "duration_minutes": 45,
            },
            {
                "name": "Маникюр классический",
                "description": "Обработка ногтей и кутикулы",
                "category": ServiceCategory.NAILS,
                "price": 1500,
                "duration_minutes": 90,
            },
            {
                "name": "Педикюр",
                "description": "Полная обработка стоп и ногтей",
                "category": ServiceCategory.NAILS,
                "price": 2200,
                "duration_minutes": 120,
            },
            {
                "name": "Визаж дневной",
                "description": "Лёгкий дневной макияж",
                "category": ServiceCategory.MAKEUP,
                "price": 2000,
                "duration_minutes": 60,
            },
            {
                "name": "Визаж вечерний",
                "description": "Праздничный макияж с учётом образа",
                "category": ServiceCategory.MAKEUP,
                "price": 3500,
                "duration_minutes": 90,
            },
            {
                "name": "Чистка лица",
                "description": "Глубокая очистка кожи",
                "category": ServiceCategory.FACIAL,
                "price": 4000,
                "duration_minutes": 120,
            },
            {
                "name": "SPA-уход",
                "description": "Комплексный уход за телом",
                "category": ServiceCategory.SPA,
                "price": 5000,
                "duration_minutes": 150,
            },
        ]

        for service_data in services_data:
            result = await db.execute(
                select(Service).where(Service.name == service_data["name"])
            )
            existing = result.scalar_one_or_none()
            
            if not existing:
                service = Service(**service_data)
                db.add(service)
                print(f"✅ Добавлена услуга: {service_data['name']}")
            else:
                print(f"⏭️  Пропущено: {service_data['name']} (уже есть)")

        await db.commit()

        # === Мастера ===
        masters_data = [
            {
                "name": "Анна Смирнова",
                "specialty": "Топ-стилист, колорист",
                "description": "Опыт работы 8 лет. Специализируется на сложных окрашиваниях.",
                "photo_url": "https://image.qwenlm.ai/public_source/bf7b0364-fbcc-4b04-a11e-20ea9271eb00/16ae52de6-8eb5-4881-a3fa-87167197d78b.png",
                "rating": 4.9,
            },
            {
                "name": "Мария Козлова",
                "specialty": "Мастер маникюра и педикюра",
                "description": "Опыт работы 5 лет. Владеет всеми современными техниками.",
                "photo_url": "https://image.qwenlm.ai/public_source/bf7b0364-fbcc-4b04-a11e-20ea9271eb00/16ae52de6-8eb5-4881-a3fa-87167197d78b.png",
                "rating": 4.8,
            },
            {
                "name": "Елена Воронова",
                "specialty": "Визажист",
                "description": "Опыт работы 6 лет. Работала на неделях моды.",
                "photo_url": "https://image.qwenlm.ai/public_source/bf7b0364-fbcc-4b04-a11e-20ea9271eb00/16ae52de6-8eb5-4881-a3fa-87167197d78b.png",
                "rating": 5.0,
            },
            {
                "name": "Ольга Петрова",
                "specialty": "Косметолог",
                "description": "Врач-косметолог с опытом 10 лет.",
                "photo_url": "https://image.qwenlm.ai/public_source/bf7b0364-fbcc-4b04-a11e-20ea9271eb00/16ae52de6-8eb5-4881-a3fa-87167197d78b.png",
                "rating": 4.9,
            },
        ]

        for master_data in masters_data:
            result = await db.execute(
                select(Master).where(Master.name == master_data["name"])
            )
            existing = result.scalar_one_or_none()
            
            if not existing:
                master = Master(**master_data)
                db.add(master)
                print(f"✅ Добавлен мастер: {master_data['name']}")
            else:
                print(f"⏭️  Пропущено: {master_data['name']} (уже есть)")

        await db.commit()

        # === Портфолио ===
        portfolio_data = [
            {
                "title": "Вечерняя причёска",
                "description": "Свадебная укладка с локонами",
                "category": ServiceCategory.HAIR,
                "image_url": "https://image.qwenlm.ai/public_source/bf7b0364-fbcc-4b04-a11e-20ea9271eb00/16ae52de6-8eb5-4881-a3fa-87167197d78b.png",
                "is_featured": True,
            },
            {
                "title": "Французский маникюр",
                "description": "Классический френч с дизайном",
                "category": ServiceCategory.NAILS,
                "image_url": "https://image.qwenlm.ai/public_source/bf7b0364-fbcc-4b04-a11e-20ea9271eb00/16ae52de6-8eb5-4881-a3fa-87167197d78b.png",
                "is_featured": True,
            },
            {
                "title": "Свадебный макияж",
                "description": "Нежный образ для невесты",
                "category": ServiceCategory.MAKEUP,
                "image_url": "https://image.qwenlm.ai/public_source/bf7b0364-fbcc-4b04-a11e-20ea9271eb00/16ae52de6-8eb5-4881-a3fa-87167197d78b.png",
                "is_featured": True,
            },
            {
                "title": "Омолаживающая процедура",
                "description": "Результат после курса процедур",
                "category": ServiceCategory.FACIAL,
                "image_url": "https://image.qwenlm.ai/public_source/bf7b0364-fbcc-4b04-a11e-20ea9271eb00/16ae52de6-8eb5-4881-a3fa-87167197d78b.png",
                "is_featured": False,
            },
            {
                "title": "Креативное окрашивание",
                "description": "Окрашивание в технике AirTouch",
                "category": ServiceCategory.HAIR,
                "image_url": "https://image.qwenlm.ai/public_source/bf7b0364-fbcc-4b04-a11e-20ea9271eb00/16ae52de6-8eb5-4881-a3fa-87167197d78b.png",
                "is_featured": False,
            },
            {
                "title": "Дизайн ногтей",
                "description": "Авторский дизайн с росписью",
                "category": ServiceCategory.NAILS,
                "image_url": "https://image.qwenlm.ai/public_source/bf7b0364-fbcc-4b04-a11e-20ea9271eb00/16ae52de6-8eb5-4881-a3fa-87167197d78b.png",
                "is_featured": False,
            },
        ]

        for portfolio_item in portfolio_data:
            result = await db.execute(
                select(PortfolioItem).where(
                    PortfolioItem.title == portfolio_item["title"],
                    PortfolioItem.category == portfolio_item["category"]
                )
            )
            existing = result.scalar_one_or_none()
            
            if not existing:
                item = PortfolioItem(**portfolio_item)
                db.add(item)
                print(f"✅ Добавлено портфолио: {portfolio_item['title']}")
            else:
                print(f"⏭️  Пропущено: {portfolio_item['title']} (уже есть)")

        await db.commit()

        # === Контакты ===
        contact_result = await db.execute(select(ContactInfo))
        contact = contact_result.scalar_one_or_none()
        
        if not contact:
            contact_info = ContactInfo(
                address="г. Москва, ул. 2-я Карачаровская, д. 16/2",
                phone="+7 (916) 818-27-77",
                email="info@beautysalon.ru",
                working_hours="Пн-Вс: 10:00 - 22:00",
                latitude=55.7558,
                longitude=37.6173,
                social_telegram="https://t.me/beautysalon",
                social_instagram="https://instagram.com/beautysalon",
                social_vk="https://vk.com/beautysalon",
            )
            db.add(contact_info)
            print("✅ Добавлена контактная информация")
            await db.commit()
        else:
            print("⏭️  Пропущено: контакты (уже есть)")

        print("\n🎉 Наполнение базы завершено!")


if __name__ == "__main__":
    asyncio.run(seed_data())
