import os
import dotenv

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.engine import URL

from bot.database.models import Base

dotenv.load_dotenv()

# database_driver = "asyncpg"
# database_system = "postgresql"

# url = URL.create(
#     drivername=f"{database_system}+{database_driver}",
#     database=os.getenv("POSTGRES_DATABASE"),
#     username=os.getenv("POSTGRES_USER", "docker"),
#     password=os.getenv("POSTGRES_PASSWORD", None),
#     port=int(os.getenv("POSTGRES_PORT", 5432)),
#     host=os.getenv("POSTGRES_HOST", "db"),
# )

url = "sqlite+aiosqlite:///bot/database/db.sqlite3"


engine = create_async_engine(url, echo=False)
session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# async def drop_db():
#     async with engine.begin() as conn:
#         await conn.execute(text("DROP SCHEMA public CASCADE"))
#         await conn.execute(text("CREATE SCHEMA public"))
