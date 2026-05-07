from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

# Строка подключения для PostgreSQl
# prod
# DATABASE_URL = "postgresql+asyncpg://ecommerce_user:xxxxxxxx@db:5432/ecommerce_db"
# local
DATABASE_URL = "postgresql+asyncpg://sessionauth_user:12345@localhost:5432/sessionauth_db"

async_engine = create_async_engine(DATABASE_URL, echo=True)

async_session_maker = async_sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)


class Base(DeclarativeBase):
    pass