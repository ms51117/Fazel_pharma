# from sqlmodel import create_engine,SQLModel
# from sqlmodel.ext.asyncio.session import AsyncSession
# from sqlalchemy.ext.asyncio import AsyncEngine
# from sqlalchemy.orm import sessionmaker
#
#
# db_url= "postgresql+asyncpg://postgres:Mehr3223@localhost:5432/Pharma_DB"
# engine = AsyncEngine(create_engine(db_url))
#
#
#
# async def create_db_table():
#     async with engine.begin() as conn:
#         await conn.run_sync(SQLModel.metadata.create_all)
#
# async def get_session():
#     async_session = sessionmaker(engine,class_=AsyncSession,expire_on_commit=False)
#     async with async_session() as session:
#         yield session

# ----------------------------------------------------------------------------------------------

# database.py

from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator
from sqlmodel import SQLModel

# Import the settings instance from our new config file
from setting import settings

# The database URL is now read securely from the settings
DATABASE_URL = settings.ASYNC_DATABASE_URI

# Create the async engine with the URL
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

async def init_db():
    """
    Initialize the database and create tables.
    """
    async with engine.begin() as conn:
        # await conn.run_sync(SQLModel.metadata.drop_all) # Uncomment to drop all tables
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get a new database session per request.
    """
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
