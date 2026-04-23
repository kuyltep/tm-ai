from fastapi import APIRouter
from app.api.v1 import v1_router

from app.exceptions import BaseErrorResponse

COMMON_RESPONSES = {
  400: {"model": BaseErrorResponse},
  401: {"model": BaseErrorResponse},
  404: {"model": BaseErrorResponse},
  422: {"model": BaseErrorResponse},
  500: {"model": BaseErrorResponse},
}

api_router = APIRouter(prefix="/api")
api_router.include_router(v1_router)
