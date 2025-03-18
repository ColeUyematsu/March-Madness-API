from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Create session factory
SessionFactory = async_sessionmaker(engine, expire_on_commit=False)

# Dependency to get DB session
async def get_db() -> AsyncSession:
    async with SessionFactory() as session:
        yield session
