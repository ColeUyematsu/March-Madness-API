from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db

class BaseHandler:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db
