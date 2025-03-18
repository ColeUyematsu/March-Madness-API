from fastapi import APIRouter, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.api.base import BaseHandler
from backend.models.matchup import Matchup
import json

router = APIRouter()

class MatchupHandler(BaseHandler):
    """Handles database queries related to matchups."""

    async def get_matchups(self, start_year: int = None, end_year: int = None):
        query = select(Matchup)
        if start_year and end_year:
            query = query.where(Matchup.year.between(start_year, end_year))
            
        result = await self.db.execute(query)
        matchups = result.scalars().all()

        # Convert NaN values to None (JSON-compatible)
        matchups_clean = json.loads(json.dumps([m.__dict__ for m in matchups], default=str))
        for matchup in matchups_clean:
            for key, value in matchup.items():
                if isinstance(value, float) and (value != value):  # NaN check
                    matchup[key] = None

        return matchups_clean

@router.get("/")
async def get_matchups(
    start_year: int = Query(None, description="Start Year of Matchups"),
    end_year: int = Query(None, description="End Year of Matchups"),
    handler: MatchupHandler = Depends()
):
    """Fetch matchups from the database, optionally filtered by year."""
    matchups = await handler.get_matchups(start_year, end_year)
    return {"matchups": matchups}
