from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db.database import close_database


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
  yield
  await close_database()
