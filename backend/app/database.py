from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text
from app.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=True)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    async with engine.begin() as conn:
        # Add new enum values if they don't exist (PostgreSQL specific)
        new_types = [
            'python', 'databases_messaging',
            'devops', 'ai_llm', 'system_concepts'
        ]
        for val in new_types:
            await conn.execute(text(
                f"ALTER TYPE interviewtype ADD VALUE IF NOT EXISTS '{val}'"
            ))
        await conn.run_sync(Base.metadata.create_all)
