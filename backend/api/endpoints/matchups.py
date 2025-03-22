from fastapi import APIRouter, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.api.base import BaseHandler
from backend.models.matchup import Matchup
import json
from backend.models.team_stats import TeamStats
import itertools

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

    async def get_round_of_64_matchups(self):
            """Fetches the round of 64 matchups for 2025 with scores and stats."""
            # Define the round of 64 matchups based on the provided data
            round_of_64_matchups = [
                {"teamA": "Creighton", "teamB": "Louisville", "seed_teamA": 9, "seed_teamB": 8, "score_teamA": 89, "score_teamB": 75, "day": "Thursday", "date": "March 20"},
                {"teamA": "Purdue", "teamB": "High Point", "seed_teamA": 4, "seed_teamB": 13, "score_teamA": 75, "score_teamB": 63, "day": "Thursday", "date": "March 20"},
                {"teamA": "Wisconsin", "teamB": "Montana", "seed_teamA": 3, "seed_teamB": 14, "score_teamA": 85, "score_teamB": 66, "day": "Thursday", "date": "March 20"},
                {"teamA": "Houston", "teamB": "SIU Edwardsville", "seed_teamA": 1, "seed_teamB": 16, "score_teamA": 78, "score_teamB": 40, "day": "Thursday", "date": "March 20"},
                {"teamA": "Auburn", "teamB": "Alabama State", "seed_teamA": 1, "seed_teamB": 16, "score_teamA": 83, "score_teamB": 63, "day": "Thursday", "date": "March 20"},
                {"teamA": "McNeese", "teamB": "Clemson", "seed_teamA": 12, "seed_teamB": 5, "score_teamA": 69, "score_teamB": 67, "day": "Thursday", "date": "March 20"},
                {"teamA": "BYU", "teamB": "VCU", "seed_teamA": 6, "seed_teamB": 11, "score_teamA": 80, "score_teamB": 71, "day": "Thursday", "date": "March 20"},
                {"teamA": "Gonzaga", "teamB": "Georgia", "seed_teamA": 8, "seed_teamB": 9, "score_teamA": 89, "score_teamB": 68, "day": "Thursday", "date": "March 20"},
                {"teamA": "Tennessee", "teamB": "Wofford", "seed_teamA": 2, "seed_teamB": 15, "score_teamA": 77, "score_teamB": 62, "day": "Thursday", "date": "March 20"},
                {"teamA": "Arkansas", "teamB": "Kansas", "seed_teamA": 10, "seed_teamB": 7, "score_teamA": 79, "score_teamB": 72, "day": "Thursday", "date": "March 20"},
                {"teamA": "Texas A&M", "teamB": "Yale", "seed_teamA": 4, "seed_teamB": 13, "score_teamA": 80, "score_teamB": 71, "day": "Thursday", "date": "March 20"},
                {"teamA": "Drake", "teamB": "Missouri", "seed_teamA": 11, "seed_teamB": 6, "score_teamA": 67, "score_teamB": 57, "day": "Thursday", "date": "March 20"},
                {"teamA": "UCLA", "teamB": "Utah State", "seed_teamA": 7, "seed_teamB": 10, "score_teamA": 72, "score_teamB": 47, "day": "Thursday", "date": "March 20"},
                {"teamA": "St. John's", "teamB": "Omaha", "seed_teamA": 2, "seed_teamB": 15, "score_teamA": 83, "score_teamB": 53, "day": "Thursday", "date": "March 20"},
                {"teamA": "Michigan", "teamB": "UC San Diego", "seed_teamA": 5, "seed_teamB": 12, "score_teamA": 68, "score_teamB": 65, "day": "Thursday", "date": "March 20"},
                {"teamA": "Texas Tech", "teamB": "UNC Wilmington", "seed_teamA": 3, "seed_teamB": 14, "score_teamA": 82, "score_teamB": 72, "day": "Thursday", "date": "March 20"},
                
                {"teamA": "Baylor", "teamB": "Mississippi State", "seed_teamA": 9, "seed_teamB": 8, "score_teamA": 75, "score_teamB": 72, "day": "Friday", "date": "March 21"},
                {"teamA": "Alabama", "teamB": "Robert Morris", "seed_teamA": 2, "seed_teamB": 15, "score_teamA": 90, "score_teamB": 81, "day": "Friday", "date": "March 21"},
                {"teamA": "Iowa State", "teamB": "Lipscomb", "seed_teamA": 3, "seed_teamB": 14, "score_teamA": 82, "score_teamB": 55, "day": "Friday", "date": "March 21"},
                {"teamA": "Colorado State", "teamB": "Memphis", "seed_teamA": 12, "seed_teamB": 5, "score_teamA": 78, "score_teamB": 70, "day": "Friday", "date": "March 21"},
                {"teamA": "Duke", "teamB": "Mount St. Mary's", "seed_teamA": 1, "seed_teamB": 16, "score_teamA": 93, "score_teamB": 49, "day": "Friday", "date": "March 21"},
                {"teamA": "Saint Mary's", "teamB": "Vanderbilt", "seed_teamA": 7, "seed_teamB": 10, "score_teamA": 59, "score_teamB": 56, "day": "Friday", "date": "March 21"},
                {"teamA": "Ole Miss", "teamB": "North Carolina", "seed_teamA": 6, "seed_teamB": 11, "score_teamA": 71, "score_teamB": 64, "day": "Friday", "date": "March 21"},
                {"teamA": "Maryland", "teamB": "Grand Canyon", "seed_teamA": 4, "seed_teamB": 13, "score_teamA": 81, "score_teamB": 49, "day": "Friday", "date": "March 21"},
                {"teamA": "Florida", "teamB": "Norfolk State", "seed_teamA": 1, "seed_teamB": 16, "score_teamA": 95, "score_teamB": 69, "day": "Friday", "date": "March 21"},
                {"teamA": "Kentucky", "teamB": "Troy", "seed_teamA": 3, "seed_teamB": 14, "score_teamA": 76, "score_teamB": 57, "day": "Friday", "date": "March 21"},
                {"teamA": "New Mexico", "teamB": "Marquette", "seed_teamA": 10, "seed_teamB": 7, "score_teamA": 75, "score_teamB": 66, "day": "Friday", "date": "March 21"},
                {"teamA": "Arizona", "teamB": "Akron", "seed_teamA": 4, "seed_teamB": 13, "score_teamA": 93, "score_teamB": 65, "day": "Friday", "date": "March 21"},
                {"teamA": "UConn", "teamB": "Oklahoma", "seed_teamA": 8, "seed_teamB": 9, "score_teamA": 67, "score_teamB": 59, "day": "Friday", "date": "March 21"},
                {"teamA": "Illinois", "teamB": "Xavier", "seed_teamA": 6, "seed_teamB": 11, "score_teamA": 86, "score_teamB": 73, "day": "Friday", "date": "March 21"},
                {"teamA": "Michigan State", "teamB": "Bryant", "seed_teamA": 2, "seed_teamB": 15, "score_teamA": 87, "score_teamB": 62, "day": "Friday", "date": "March 21"},
                {"teamA": "Oregon", "teamB": "Liberty", "seed_teamA": 5, "seed_teamB": 12, "score_teamA": 81, "score_teamB": 52, "day": "Friday", "date": "March 21"}
            ]
            
            # Format the matchups with a simplified stats lookup (no database saving)
            formatted_matchups = []
            
            for matchup in round_of_64_matchups:
                # Create a formatted matchup that focuses on display-friendly data
                formatted_matchup = {
                    "matchup_display": f"({matchup['seed_teamA']}) {matchup['teamA']} vs ({matchup['seed_teamB']}) {matchup['teamB']}",
                    "result": f"({matchup['seed_teamA']}) {matchup['teamA']} {matchup['score_teamA']} - {matchup['score_teamB']} ({matchup['seed_teamB']}) {matchup['teamB']}",
                    "winner": matchup["teamA"] if matchup["score_teamA"] > matchup["score_teamB"] else matchup["teamB"],
                    "upset": (matchup["seed_teamA"] > matchup["seed_teamB"] and matchup["score_teamA"] > matchup["score_teamB"]) or 
                            (matchup["seed_teamB"] > matchup["seed_teamA"] and matchup["score_teamB"] > matchup["score_teamA"]),
                    "teamA": {
                        "name": matchup["teamA"],
                        "seed": matchup["seed_teamA"],
                        "score": matchup["score_teamA"]
                    },
                    "teamB": {
                        "name": matchup["teamB"],
                        "seed": matchup["seed_teamB"],
                        "score": matchup["score_teamB"]
                    },
                    "point_difference": abs(matchup["score_teamA"] - matchup["score_teamB"]),
                    "round_name": "Round of 64"
                }
                
                # Try to get additional stats if available (but don't fail if they're not)
                try:
                    matchup_stats = await self.get_matchup_stats(matchup["teamA"], matchup["teamB"])
                    
                    if isinstance(matchup_stats, dict):
                        # Add the key differential stats (only the most important ones)
                        formatted_matchup["key_stats"] = {
                            "diff_win_pct": matchup_stats.get("diff_win_pct"),
                            "diff_srs": matchup_stats.get("diff_srs"),
                            "diff_ps_per_game": matchup_stats.get("diff_ps_per_game"),
                            "diff_pa_per_game": matchup_stats.get("diff_pa_per_game"),
                            "diff_fg_pct": matchup_stats.get("diff_fg_pct"),
                            "diff_fg3_pct": matchup_stats.get("diff_fg3_pct")
                        }
                        
                        # Include full stats for those who want more detail
                        formatted_matchup["full_stats"] = {k: v for k, v in matchup_stats.items() 
                                                        if k.startswith("diff_") and v is not None}
                except:
                    # If stats lookup fails, just continue with the basic matchup info
                    formatted_matchup["stats_available"] = False
                
                formatted_matchups.append(formatted_matchup)
            
            return formatted_matchups
    async def get_round_of_32_matchups(self):
        """Fetches the round of 32 matchups for 2025 with projected stats (no results)."""
        round_of_32_matchups = [
            # Saturday, March 22
            {"teamA": "Purdue", "teamB": "McNeese", "seed_teamA": 4, "seed_teamB": 12, "day": "Saturday", "date": "March 22"},
            {"teamA": "St. John's", "teamB": "Arkansas", "seed_teamA": 2, "seed_teamB": 10, "day": "Saturday", "date": "March 22"},
            {"teamA": "Texas A&M", "teamB": "Michigan", "seed_teamA": 4, "seed_teamB": 5, "day": "Saturday", "date": "March 22"},
            {"teamA": "Texas Tech", "teamB": "Drake", "seed_teamA": 3, "seed_teamB": 11, "day": "Saturday", "date": "March 22"},
            {"teamA": "Auburn", "teamB": "Creighton", "seed_teamA": 1, "seed_teamB": 9, "day": "Saturday", "date": "March 22"},
            {"teamA": "Wisconsin", "teamB": "BYU", "seed_teamA": 3, "seed_teamB": 6, "day": "Saturday", "date": "March 22"},
            {"teamA": "Houston", "teamB": "Gonzaga", "seed_teamA": 1, "seed_teamB": 8, "day": "Saturday", "date": "March 22"},
            {"teamA": "Tennessee", "teamB": "UCLA", "seed_teamA": 2, "seed_teamB": 7, "day": "Saturday", "date": "March 22"},
            # Sunday, March 23
            {"teamA": "Florida", "teamB": "UConn", "seed_teamA": 1, "seed_teamB": 8, "day": "Sunday", "date": "March 23"},
            {"teamA": "Duke", "teamB": "Baylor", "seed_teamA": 1, "seed_teamB": 9, "day": "Sunday", "date": "March 23"},
            {"teamA": "Kentucky", "teamB": "Illinois", "seed_teamA": 3, "seed_teamB": 6, "day": "Sunday", "date": "March 23"},
            {"teamA": "Alabama", "teamB": "Saint Mary's", "seed_teamA": 2, "seed_teamB": 7, "day": "Sunday", "date": "March 23"},
            {"teamA": "Maryland", "teamB": "Colorado State", "seed_teamA": 4, "seed_teamB": 12, "day": "Sunday", "date": "March 23"},
            {"teamA": "Iowa State", "teamB": "Ole Miss", "seed_teamA": 3, "seed_teamB": 6, "day": "Sunday", "date": "March 23"},
            {"teamA": "Michigan State", "teamB": "New Mexico", "seed_teamA": 2, "seed_teamB": 10, "day": "Sunday", "date": "March 23"},
            {"teamA": "Arizona", "teamB": "Oregon", "seed_teamA": 4, "seed_teamB": 5, "day": "Sunday", "date": "March 23"},
        ]

        formatted_matchups = []

        for matchup in round_of_32_matchups:
            formatted = {
                "matchup_display": f"({matchup['seed_teamA']}) {matchup['teamA']} vs ({matchup['seed_teamB']}) {matchup['teamB']}",
                "teamA": {
                    "name": matchup["teamA"],
                    "seed": matchup["seed_teamA"]
                },
                "teamB": {
                    "name": matchup["teamB"],
                    "seed": matchup["seed_teamB"]
                },
            }

            try:
                matchup_stats = await self.get_matchup_stats(matchup["teamA"], matchup["teamB"])
                if isinstance(matchup_stats, dict):
                    formatted["key_stats"] = {
                        "diff_win_pct": matchup_stats.get("diff_win_pct"),
                        "diff_srs": matchup_stats.get("diff_srs"),
                        "diff_ps_per_game": matchup_stats.get("diff_ps_per_game"),
                        "diff_pa_per_game": matchup_stats.get("diff_pa_per_game"),
                        "diff_fg_pct": matchup_stats.get("diff_fg_pct"),
                        "diff_fg3_pct": matchup_stats.get("diff_fg3_pct")
                    }
                    formatted["full_stats"] = {
                        k: v for k, v in matchup_stats.items()
                        if k.startswith("diff_") and v is not None
                    }
            except Exception as e:
                formatted["stats_available"] = False
                formatted["error"] = str(e)

            formatted_matchups.append(formatted)

        return formatted_matchups
    
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

@router.get("/2025/round64")
async def get_all_2025_matchups(
   handler: MatchupHandler = Depends()
):
    """Fetch the round of 64 matchups and results for 2025."""
    matchups = await handler.get_round_of_64_matchups()
    
    # Generate some summary statistics about the matchups
    total_games = len(matchups)
    upsets = sum(1 for m in matchups if m.get("upset", False))
    avg_point_difference = sum(m.get("point_difference", 0) for m in matchups) / total_games if total_games > 0 else 0
    
    return {
        "summary": {
            "total_games": total_games,
            "upsets": upsets,
            "upset_percentage": round(upsets / total_games * 100, 1) if total_games > 0 else 0,
            "avg_point_difference": round(avg_point_difference, 1),
        },
        "round_of_64_matchups": matchups,

    }

@router.get("/2025/round32")
async def get_all_round_of_32_matchups(
    handler: MatchupHandler = Depends()
):
    """API route for Round of 32 projected stats (no results)."""
    matchups = await handler.get_round_of_32_matchups()
    return {"round_of_32_matchups": matchups}
