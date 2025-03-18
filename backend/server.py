from fastapi import FastAPI
from app.api.v1.endpoints import items

app = FastAPI()

# Include API routes
app.include_router(items.router, prefix="/items", tags=["items"])

@app.on_event("shutdown")
async def shutdown():
    from app.core.database import engine
    await engine.dispose()