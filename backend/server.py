from fastapi import FastAPI
from backend.api.endpoints.matchups import router as matchups_router
from backend.api.endpoints.team_stats import router as team_stats_router  # ✅ Import team_stats router

app = FastAPI()

app.include_router(matchups_router, prefix="/matchups", tags=["matchups"])
app.include_router(team_stats_router, prefix="/stats", tags=["team stats"])  # ✅ Register team_stats router

# Include API routes
# use include_router on all routes we are using

@app.get("/")
async def root():
    return "API running"

@app.on_event("shutdown")
async def shutdown():
    from app.core.database import engine
    await engine.dispose()