from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.api.v1.analyze.schemas import AnalysisResponse, CreateAnalysisResponse
from app.api.v1.analyze.service import analysis_service
from app.api.deps import check_api_key, get_session_factory
from app.db import get_db
from app.exceptions import NotFoundAppError

from app.api.responses import COMMON_RESPONSES

router = APIRouter(prefix="/analyses", tags=["analyses"], dependencies=[Depends(check_api_key)])


@router.post(
  "", response_model=CreateAnalysisResponse, status_code=status.HTTP_202_ACCEPTED, responses=COMMON_RESPONSES
)
async def create_analysis(
  background_tasks: BackgroundTasks,
  files: list[UploadFile] = File(..., description="One or more audio/video files"),
  user_id: UUID | None = Form(default=None),
  session_factory: async_sessionmaker[AsyncSession] = Depends(get_session_factory),
  db: AsyncSession = Depends(get_db),
) -> CreateAnalysisResponse:
  return await analysis_service.create_analyses(
    db,
    files=files,
    user_id=user_id,
    background_tasks=background_tasks,
    session_factory=session_factory,
  )


@router.get("/{analysis_id}", response_model=AnalysisResponse, responses=COMMON_RESPONSES)
async def get_analysis(
  analysis_id: UUID,
  db: AsyncSession = Depends(get_db),
) -> AnalysisResponse:
  analysis = await analysis_service.get_analysis(db, analysis_id)
  if analysis is None:
    raise NotFoundAppError("Analysis not found")
  return analysis
