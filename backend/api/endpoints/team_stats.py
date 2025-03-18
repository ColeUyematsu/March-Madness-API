from fastapi import APIRouter, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.api.base import BaseHandler
from backend.models.team_stats import TeamStats
import json

router = APIRouter()

class TeamStatsHandler(BaseHandler):
    """Handles database queries related to team stats."""

    async def get_team_stats(self, start_year: int = None, end_year: int = None, team: str = None):
        query = select(TeamStats)

        if start_year and end_year:
            query = query.where(TeamStats.year.between(start_year, end_year))
        elif start_year:  # Allow single year selection
            query = query.where(TeamStats.year == start_year)

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
    start_year: int = Query(None, description="Filter by Start Year"),
    end_year: int = Query(None, description="Filter by End Year"),
    team: str = Query(None, description="Filter by Team Name"),
    handler: TeamStatsHandler = Depends()
):
    """Fetch team stats from the database, optionally filtered by a range of years or team name."""
    team_stats = await handler.get_team_stats(start_year, end_year, team)
    return {"team_stats": team_stats}

@router.get("/year/{year}")
async def get_team_stats_by_year(
    year: int,
    handler: TeamStatsHandler = Depends()
):
    """Fetch team stats for a specific year."""
    team_stats = await handler.get_team_stats(start_year=year, end_year=year)
    return {"team_stats": team_stats}