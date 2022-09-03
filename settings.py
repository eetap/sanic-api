from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import AsyncSession

bind = create_async_engine("postgresql+asyncpg://postgres:123@localhost/test", echo=True)

async_session = sessionmaker(bind, AsyncSession, expire_on_commit=False)