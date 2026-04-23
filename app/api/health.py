from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.db import check_database
from app.exceptions import BaseErrorResponse

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
  status: str


@router.get("/health", response_model=HealthResponse, responses={503: {"model": BaseErrorResponse}})
async def health() -> HealthResponse:
  try:
    await check_database()
  except Exception as exc:
    raise HTTPException(
      status_code=503,
      detail={"code": "service_unavailable", "message": "Database is unavailable", "details": {"status": "error"}},
    ) from exc
  return HealthResponse(status="ok")
