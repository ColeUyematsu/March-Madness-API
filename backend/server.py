from fastapi import FastAPI
from backend.api.endpoints.matchups import router as matchups_router

app = FastAPI()

app.include_router(matchups_router, prefix="/matchups", tags=["matchups"])

# Include API routes
# use include_router on all routes we are using

@app.on_event("shutdown")
async def shutdown():
    from app.core.database import engine
    await engine.dispose()