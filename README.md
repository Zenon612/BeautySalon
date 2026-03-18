# BeautySalon API

Backend + Light Front как сайт-визитка для салона красоты на FastAPI + PostgreSQL.

## Технологии
- 🐍 Python 3.11+
- ⚡ FastAPI (асинхронный)
- 🗄️ PostgreSQL + SQLAlchemy 2.0
- 🔐 JWT аутентификация
- 🧪 Тесты: pytest + httpx

## Установка
```bash
# 1. Клонировать репозиторий
git clone https://github.com/your-username/beautysalon-api.git
cd beautysalon-api

# 2. Создать виртуальное окружение
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# или
.venv\Scripts\activate     # Windows

# 3. Установить зависимости
pip install -r requirements.txt

# 4. Настроить окружение
cp .env.example .env
# Отредактировать .env

# 5. Применить миграции
alembic upgrade head

# 6. Запустить сервер
uvicorn app.main:app --reload