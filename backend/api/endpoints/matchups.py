from fastapi import APIRouter, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.api.base import BaseHandler
from backend.models.matchup import Matchup

router = APIRouter()

class MatchupHandler(BaseHandler):
    """Handles database queries related to matchups."""

    async def get_matchups(self, start_year: int = None, end_year: int = None):
        query = select(Matchup)
        if start_year and end_year:
            query = query.where(Matchup.year.between(start_year, end_year))
            
        result = await self.db.execute(query)
        return result.scalars().all()

@router.get("/")
async def get_matchups(
    start_year: int = Query(None, description="Start Year of Matchups"),
    end_year: int = Query(None, description="End Year of Matchups"),
    handler: MatchupHandler = Depends()
):
    """Fetch matchups from the database, optionally filtered by year."""
    matchups = await handler.get_matchups(start_year, end_year)
    return {"matchups": matchups}
