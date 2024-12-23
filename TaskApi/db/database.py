from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

DATABASE_URL = "postgresql+asyncpg://postgres_admin:postgres_33rfdf322@postgres:5432/postgres"

engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db_session():
    async with SessionLocal() as session:
        return  session
