from fastapi import APIRouter, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.api.base import BaseHandler
from backend.models.team_stats import TeamStats
import json

router = APIRouter()

class TeamStatsHandler(BaseHandler):
    """Handles database queries related to team stats."""

    async def get_team_stats(self, year: int = None, team: str = None):
        query = select(TeamStats)

        if year:
            query = query.where(TeamStats.year == year)
        if team:
            query = query.where(TeamStats.team.ilike(f"%{team}%"))  # Case-insensitive search

        result = await self.db.execute(query)
        teams = result.scalars().all()

        # Convert to JSON-safe format
        teams_clean = json.loads(json.dumps([t.__dict__ for t in teams], default=str))
        for team in teams_clean:
            for key, value in team.items():
                if isinstance(value, float) and (value != value):  # NaN check
                    team[key] = None

        return teams_clean

@router.get("/")
async def get_team_stats(
    year: int = Query(None, description="Filter by Year"),
    team: str = Query(None, description="Filter by Team Name"),
    handler: TeamStatsHandler = Depends()
):
    """Fetch team stats from the database, optionally filtered by year or team."""
    team_stats = await handler.get_team_stats(year, team)
    return {"team_stats": team_stats}