from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Matchup(Base):
    __tablename__ = "matchups"

    id = Column(Integer, primary_key=True, autoincrement=True)  # Auto-generated ID
    year = Column(Integer, nullable=False)
    teamA = Column(String, nullable=False)
    teamB = Column(String, nullable=False)
    winner = Column(Integer, nullable=False)
    diff_seed = Column(Integer, nullable=False)
    diff_win_pct = Column(Float, nullable=False)
    diff_ps_per_game = Column(Float, nullable=False)
    diff_pa_per_game = Column(Float, nullable=False)
    diff_srs = Column(Float, nullable=False)
    diff_sos = Column(Float, nullable=False)
    diff_fg_per_game = Column(Float, nullable=False)
    diff_fga_per_game = Column(Float, nullable=False)
    diff_fg_pct = Column(Float, nullable=False)
    diff_fg2_per_game = Column(Float, nullable=False)
    diff_fg2a_per_game = Column(Float, nullable=False)
    diff_fg2_pct = Column(Float, nullable=False)
    diff_fg3_per_game = Column(Float, nullable=False)
    diff_fg3a_per_game = Column(Float, nullable=False)
    diff_fg3_pct = Column(Float, nullable=False)
    diff_ft_per_game = Column(Float, nullable=False)
    diff_fta_per_game = Column(Float, nullable=False)
    diff_ft_pct = Column(Float, nullable=False)
    diff_orb_per_game = Column(Float, nullable=False)
    diff_drb_per_game = Column(Float, nullable=False)
    diff_trb_per_game = Column(Float, nullable=False)
    diff_ast_per_game = Column(Float, nullable=False)
    diff_stl_per_game = Column(Float, nullable=False)
    diff_blk_per_game = Column(Float, nullable=False)
    diff_tov_per_game = Column(Float, nullable=False)
    diff_pf_per_game = Column(Float, nullable=False)
    diff_offensive_rating = Column(Float, nullable=False)
    diff_defensive_rating = Column(Float, nullable=False)
