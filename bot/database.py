from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from models import Base

DATABASE_URL = "postgresql+asyncpg://wg_forge:42a@localhost/wg_forge_db"

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if name == "__main__":
    import asyncio
    asyncio.run(init_db())