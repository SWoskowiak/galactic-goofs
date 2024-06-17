# database.py
import os
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL is None:
    raise EnvironmentError("Environment variable: 'DATABASE_URL' missing!")

SQL_ALCHEMY_ECHO = os.getenv("SQL_ALCHEMY_ECHO") == "True"

# Create an Async Engine specific for use with asyncio
engine = create_async_engine(
    DATABASE_URL,
    echo=SQL_ALCHEMY_ECHO,
    future=True,
)

# Creating a custom session class that is bound to the engine
AsyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@asynccontextmanager
async def db_session():
    """DB Session manager"""
    async with AsyncSessionLocal() as session:
        try:
            yield session  # Provide the session to the endpoint
            await session.commit()  # Commit any changes made during the request
        except Exception as e:
            await session.rollback()  # Rollback changes on error
            raise e
        finally:
            await session.close()


async def get_db_session():
    """
    Dependency function to be used in FastAPI endpoints.
    This will provide a session for each request and handle rollback/commit.
    """
    async with db_session() as session:
        yield session
