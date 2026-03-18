from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings
from sqlalchemy.pool import NullPool

class Base(DeclarativeBase):
    pass

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    poolclass=NullPool if settings.debug else None,
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_ = AsyncSession,
    expire_on_commit=False,
)
