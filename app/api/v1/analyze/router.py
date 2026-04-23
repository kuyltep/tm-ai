from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.analyze.schemas import AnalysisResponse, CreateAnalysisResponse
from app.api.v1.analyze.service import analysis_service
from app.db import get_db
from app.exceptions import NotFoundAppError

from app.api import COMMON_RESPONSES
from app.api.deps import check_api_key

router = APIRouter(prefix="/analyses", tags=["analyses"], dependencies=Depends(check_api_key))


@router.post(
  "", response_model=CreateAnalysisResponse, status_code=status.HTTP_202_ACCEPTED, responses=COMMON_RESPONSES
)
async def create_analysis(
  background_tasks: BackgroundTasks,
  files: Annotated[list[UploadFile], File(description="One or more audio/video files")],
  user_id: Annotated[UUID | None, Form()] = None,
  db: AsyncSession = Depends(get_db),
) -> CreateAnalysisResponse:
  return await analysis_service.create_analyses(
    db,
    files=files,
    user_id=user_id,
    background_tasks=background_tasks,
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
