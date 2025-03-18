from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db_conn import get_db

class BaseHandler:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db
