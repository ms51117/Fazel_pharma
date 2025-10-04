from sqlmodel import create_engine,SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.orm import sessionmaker


db_url= "postgresql+asyncpg://postgres:Mehr3223@localhost:5432/Pharma_DB"
engine = AsyncEngine(create_engine(db_url))



async def create_db_table():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_session():
    async_session = sessionmaker(engine,class_=AsyncSession,expire_on_commit=False)
    async with async_session() as session:
        yield session

