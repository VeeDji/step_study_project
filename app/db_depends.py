from sqlalchemy.orm import session, Session
from fastapi import Depends

from app.database import SessionLocal

def get_db() -> Session:
    """
    Dependency for db session
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --------------- Асинхронная сессия -------------------------

from typing import AsyncGenerator
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import async_session_maker

async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Async session with psql
    """
    async with async_session_maker() as session:
        yield session