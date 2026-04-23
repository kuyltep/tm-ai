from fastapi import APIRouter
from app.api.v1.analyze import router as analyze_router

v1_router = APIRouter(prefix="/v1")

v1_router.include_router(analyze_router)
