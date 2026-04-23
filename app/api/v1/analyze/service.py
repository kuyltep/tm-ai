import asyncio
import logging
from pathlib import Path
from uuid import UUID, uuid4

from fastapi import BackgroundTasks, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.api.v1.analyze.schemas import (
  AnalysisError,
  AnalysisErrorCode,
  AnalysisResponse,
  AnalysisStatus,
  CreateAnalysisResponse,
)
from app.exceptions import ConversionAppError, ProviderAppError, SchemaAppError, ValidationAppError
from app.llm_gateway.gemini import analyze_audio_with_cascade
from app.media import cleanup_analysis_files, convert_video_to_audio, save_upload_file, validate_content_type
from app.models.analysis import Analysis
from app.repositories import analysis_repository

logger = logging.getLogger("app.analysis")

ANALYSIS_TIMEOUT_SECONDS = 15 * 60


class AnalysisService:
  async def create_analyses(
    self,
    db: AsyncSession,
    *,
    files: list[UploadFile],
    user_id: UUID | None,
    background_tasks: BackgroundTasks,
    session_factory: async_sessionmaker[AsyncSession],
  ) -> CreateAnalysisResponse:
    if not files:
      raise ValidationAppError("At least one file is required")

    for upload in files:
      validate_content_type(upload)

    staged: list[tuple[UUID, UploadFile, Path, str]] = []
    try:
      for upload in files:
        analysis_id = uuid4()
        path, _size, content_type = await save_upload_file(upload, analysis_id)
        staged.append((analysis_id, upload, path, content_type))
    except Exception:
      for analysis_id, *_ in staged:
        cleanup_analysis_files(analysis_id)
      raise

    analyses: list[Analysis] = []
    try:
      for analysis_id, upload, _path, _content_type in staged:
        analysis = await analysis_repository.create(
          db,
          analysis_id=analysis_id,
          audio_name=upload.filename or "upload.bin",
          user_id=user_id,
          idempotency_key=None,
        )
        analyses.append(analysis)
      await db.commit()
    except Exception:
      await db.rollback()
      for analysis_id, *_ in staged:
        cleanup_analysis_files(analysis_id)
      raise

    for analysis, (_analysis_id, _upload, path, content_type) in zip(analyses, staged, strict=True):
      background_tasks.add_task(self.run_background_pipeline, analysis.id, path, content_type, session_factory)

    return CreateAnalysisResponse(analysis_id=analyses[0].id, status=AnalysisStatus.QUEUED)

  async def get_analysis(self, db: AsyncSession, analysis_id: UUID) -> AnalysisResponse | None:
    analysis = await analysis_repository.get(db, analysis_id)
    if analysis is None:
      return None
    response = AnalysisResponse.model_validate(analysis, from_attributes=True)
    if analysis.error_code or analysis.error_message:
      response = response.model_copy(
        update={
          "error": AnalysisError(
            code=AnalysisErrorCode(analysis.error_code or AnalysisErrorCode.INTERNAL_ERROR.value),
            message=analysis.error_message or "Analysis failed",
          )
        }
      )
    return response

  async def run_background_pipeline(
    self,
    analysis_id: UUID,
    source_path: Path,
    content_type: str,
    session_factory: async_sessionmaker[AsyncSession],
  ) -> None:
    attempts: list[dict] = []
    try:
      await asyncio.wait_for(
        self._run_pipeline(analysis_id, source_path, content_type, attempts, session_factory),
        timeout=ANALYSIS_TIMEOUT_SECONDS,
      )
    except TimeoutError:
      await self._mark_failed(
        analysis_id,
        AnalysisStatus.TIMED_OUT,
        AnalysisErrorCode.TIMEOUT,
        "Analysis exceeded 15 minute timeout",
        session_factory,
      )
    except ValidationAppError as exc:
      await self._mark_failed(
        analysis_id, AnalysisStatus.FAILED, AnalysisErrorCode.VALIDATION_ERROR, exc.message, session_factory
      )
    except ConversionAppError as exc:
      await self._mark_failed(
        analysis_id, AnalysisStatus.FAILED, AnalysisErrorCode.CONVERSION_ERROR, exc.message, session_factory
      )
    except SchemaAppError as exc:
      await self._mark_failed(analysis_id, AnalysisStatus.FAILED, AnalysisErrorCode.SCHEMA_ERROR, exc.message, session_factory)
    except ProviderAppError as exc:
      await self._mark_failed(
        analysis_id, AnalysisStatus.FAILED, AnalysisErrorCode.PROVIDER_ERROR, exc.message, session_factory
      )
    except Exception as exc:  # noqa: BLE001 - background jobs must never crash the server
      logger.exception("analysis pipeline failed", extra={"analysis_id": str(analysis_id)})
      await self._mark_failed(
        analysis_id,
        AnalysisStatus.FAILED,
        AnalysisErrorCode.INTERNAL_ERROR,
        str(exc),
        session_factory,
      )
    finally:
      cleanup_analysis_files(analysis_id)

  async def _run_pipeline(
    self,
    analysis_id: UUID,
    source_path: Path,
    content_type: str,
    attempts: list[dict],
    session_factory: async_sessionmaker[AsyncSession],
  ) -> None:
    async with session_factory() as db:
      await analysis_repository.set_progress(
        db,
        analysis_id,
        status=AnalysisStatus.PREPROCESSING,
        started=True,
      )
      await db.commit()

    logger.info("analysis preprocessing started", extra={"analysis_id": str(analysis_id), "stage": "preprocessing"})
    audio_path = source_path
    if content_type.startswith("video/"):
      audio_path = await convert_video_to_audio(source_path, analysis_id)

    async with session_factory() as db:
      await analysis_repository.set_progress(db, analysis_id, status=AnalysisStatus.RUNNING)
      await db.commit()

    result, _model_attempts = await analyze_audio_with_cascade(audio_path, str(analysis_id), attempts)

    async with session_factory() as db:
      await analysis_repository.complete(db, analysis_id, result=result)
      await db.commit()
    logger.info("analysis completed", extra={"analysis_id": str(analysis_id), "stage": "completed"})

  async def _mark_failed(
    self,
    analysis_id: UUID,
    status: AnalysisStatus,
    code: AnalysisErrorCode,
    message: str,
    session_factory: async_sessionmaker[AsyncSession],
  ) -> None:
    async with session_factory() as db:
      await analysis_repository.fail(db, analysis_id, status=status, code=code, message=message)
      await db.commit()
    logger.warning(
      "analysis failed",
      extra={"analysis_id": str(analysis_id), "stage": status.value},
    )


analysis_service = AnalysisService()
