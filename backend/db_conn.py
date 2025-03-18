from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
print(DATABASE_URL)

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    connect_args={"ssl": True}
)
SessionFactory = async_sessionmaker(engine, expire_on_commit=False)

# Dependency to get DB session
async def get_db() -> AsyncSession:
    async with SessionFactory() as session:
        yield session
