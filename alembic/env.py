from logging.config import fileConfig
from sqlalchemy import create_engine
from sqlalchemy import pool
from alembic import context
from app.core.config import settings
from app.db.database import Base
from app.db.models.models import (
    User,
    RefreshToken,
    Service,
    Master,
    PortfolioItem,
    ContactInfo,
)


target_metadata = Base.metadata

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

def sync_db_url() -> str:
    """
    Трансформирует ссылку на асинхронный движок под alembic
    :return: url
    """
    url = settings.database_url
    if url.startswith("postgresql+asyncpg://"):
       url = url.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
    if url.startswith("postgresql://"):
       url = url.replace("postgresql://", "postgresql+psycopg2://")
    return url

def run_migrations_offline() -> None:
    url = sync_db_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(
        sync_db_url(),
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
