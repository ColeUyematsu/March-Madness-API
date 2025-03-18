from fastapi import APIRouter, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.api.base import BaseHandler
from backend.models.matchup import Matchup
import json
from backend.models.team_stats import TeamStats

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
    
    async def get_matchup_stats(self, teamA: str, teamB: str):
        """Fetches team stats for 2025 and calculates matchup differences."""
        query = select(TeamStats).where(
            (TeamStats.year == 2025) & 
            (TeamStats.team.in_([teamA, teamB]))
        )

        result = await self.db.execute(query)
        teams = result.scalars().all()

        if len(teams) != 2:
            return "one or both of the teams not in table"

        # Assign teams dynamically
        team1, team2 = (teams[0], teams[1]) if teams[0].team == teamA else (teams[1], teams[0])

        # Compute matchup differences
        matchup_stats = {
            "year": team1.year,
            "teamA": team1.team,
            "teamB": team2.team,
            "diff_seed": (team1.seed or 0) - (team2.seed or 0),
            "diff_win_pct": (team1.win_pct or 0) - (team2.win_pct or 0),
            "diff_ps_per_game": team1.ps_per_game - team2.ps_per_game,
            "diff_pa_per_game": team1.pa_per_game - team2.pa_per_game,
            "diff_srs": team1.srs - team2.srs,
            "diff_sos": team1.sos - team2.sos,
            "diff_fg_per_game": team1.fg_per_game - team2.fg_per_game,
            "diff_fga_per_game": team1.fga_per_game - team2.fga_per_game,
            "diff_fg_pct": team1.fg_pct - team2.fg_pct,
            "diff_fg2_per_game": team1.fg2_per_game - team2.fg2_per_game,
            "diff_fg2a_per_game": team1.fg2a_per_game - team2.fg2a_per_game,
            "diff_fg2_pct": team1.fg2_pct - team2.fg2_pct,
            "diff_fg3_per_game": team1.fg3_per_game - team2.fg3_per_game,
            "diff_fg3a_per_game": team1.fg3a_per_game - team2.fg3a_per_game,
            "diff_fg3_pct": team1.fg3_pct - team2.fg3_pct,
            "diff_ft_per_game": team1.ft_per_game - team2.ft_per_game,
            "diff_fta_per_game": team1.fta_per_game - team2.fta_per_game,
            "diff_ft_pct": team1.ft_pct - team2.ft_pct,
            "diff_orb_per_game": team1.orb_per_game - team2.orb_per_game,
            "diff_drb_per_game": team1.drb_per_game - team2.drb_per_game,
            "diff_trb_per_game": team1.trb_per_game - team2.trb_per_game,
            "diff_ast_per_game": team1.ast_per_game - team2.ast_per_game,
            "diff_stl_per_game": team1.stl_per_game - team2.stl_per_game,
            "diff_blk_per_game": team1.blk_per_game - team2.blk_per_game,
            "diff_tov_per_game": team1.tov_per_game - team2.tov_per_game,
            "diff_pf_per_game": team1.pf_per_game - team2.pf_per_game,
            "diff_offensive_rating": team1.offensive_rating - team2.offensive_rating,
            "diff_defensive_rating": team1.defensive_rating - team2.defensive_rating,
        }
        matchup_stats = {k: round(v, 3) if isinstance(v, float) else v for k, v in matchup_stats.items()}

        return matchup_stats


@router.get("/")
async def get_matchups(
    start_year: int = Query(None, description="Start Year of Matchups"),
    end_year: int = Query(None, description="End Year of Matchups"),
    handler: MatchupHandler = Depends()
):
    """Fetch matchups from the database, optionally filtered by year."""
    matchups = await handler.get_matchups(start_year, end_year)
    return {"matchups": matchups}

@router.get("/year/{year}")
async def get_matchups_by_year(
    year: int,
    handler: MatchupHandler = Depends()
):
    """Fetch matchups for a specific year."""
    matchups = await handler.get_matchups(start_year=year, end_year=year)
    return {"matchups": matchups}

@router.get("/2025")
async def get_dynamic_matchup(
    teamA: str = Query(..., description="First team name"),
    teamB: str = Query(..., description="Second team name"),
    handler: MatchupHandler = Depends()
):
    """API route to get dynamically calculated matchup stats between two teams in 2025."""
    matchup_stats = await handler.get_matchup_stats(teamA, teamB)
    return {"matchup_stats": matchup_stats}