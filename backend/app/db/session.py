from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings


engine: AsyncEngine = create_async_engine(
    settings.database_url,
    pool_pre_ping=True,
)

DatabaseSessionFactory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_database_session() -> AsyncGenerator[
    AsyncSession,
    None,
]:
    session = DatabaseSessionFactory()

    try:
        yield session
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


async def check_database_connection() -> str:
    async with engine.connect() as connection:
        result = await connection.execute(
            text("SELECT current_database()"),
        )

        return str(result.scalar_one())


async def close_database_connections() -> None:
    await engine.dispose()
