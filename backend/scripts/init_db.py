'''
Just run this once to populate the matchups table
'''

import pandas as pd
import sys
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models.matchup import Matchup, Base
from backend.db_conn import engine, SessionFactory

CSV_FILE = "../fixed_matchups.csv"  # Path to your CSV file

async def create_tables():
    """Creates the matchups table."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def load_csv_data():
    """Loads data from CSV into the matchups table."""
    df = pd.read_csv(CSV_FILE)

    matchups = [Matchup(**row.to_dict()) for _, row in df.iterrows()]

    async with SessionFactory() as session:
        async with session.begin():
            session.add_all(matchups)
        await session.commit()

async def initialize_database():
    """Ensures the database is initialized and populated from CSV."""
    await create_tables()
    await load_csv_data()

if __name__ == "__main__":
    asyncio.run(initialize_database())
