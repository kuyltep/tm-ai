from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.analyze.schemas import AnalysisErrorCode, AnalysisStatus
from app.models.analysis import Analysis, utcnow


class AnalysisRepository:
  async def get(self, db: AsyncSession, analysis_id: UUID) -> Analysis | None:
    result = await db.execute(select(Analysis).where(Analysis.id == analysis_id))
    return result.scalar_one_or_none()

  async def get_by_idempotency_key(self, db: AsyncSession, idempotency_key: str) -> Analysis | None:
    result = await db.execute(select(Analysis).where(Analysis.idempotency_key == idempotency_key))
    return result.scalar_one_or_none()

  async def create(
    self,
    db: AsyncSession,
    *,
    analysis_id: UUID | None = None,
    audio_name: str,
    user_id: UUID | None,
    idempotency_key: str | None,
  ) -> Analysis:
    analysis = Analysis(
      id=analysis_id,
      audio_name=audio_name,
      user_id=user_id,
      idempotency_key=idempotency_key,
      status=AnalysisStatus.QUEUED,
      progress_stage=AnalysisStatus.QUEUED,
    )
    db.add(analysis)
    await db.flush()
    await db.refresh(analysis)
    return analysis

  async def set_progress(
    self,
    db: AsyncSession,
    analysis_id: UUID,
    *,
    status: AnalysisStatus,
    started: bool = False,
  ) -> Analysis | None:
    analysis = await self.get(db, analysis_id)
    if analysis is None:
      return None
    analysis.status = status
    analysis.progress_stage = status
    analysis.updated_at = utcnow()
    if started and analysis.started_at is None:
      analysis.started_at = utcnow()
    await db.flush()
    await db.refresh(analysis)
    return analysis

  async def complete(
    self,
    db: AsyncSession,
    analysis_id: UUID,
    *,
    result: dict,
  ) -> Analysis | None:
    analysis = await self.get(db, analysis_id)
    if analysis is None:
      return None
    analysis.status = AnalysisStatus.COMPLETED
    analysis.progress_stage = AnalysisStatus.COMPLETED
    analysis.result = result
    analysis.error_code = None
    analysis.error_message = None
    analysis.finished_at = utcnow()
    analysis.updated_at = utcnow()
    await db.flush()
    await db.refresh(analysis)
    return analysis

  async def fail(
    self,
    db: AsyncSession,
    analysis_id: UUID,
    *,
    status: AnalysisStatus,
    code: AnalysisErrorCode,
    message: str,
  ) -> Analysis | None:
    analysis = await self.get(db, analysis_id)
    if analysis is None:
      return None
    analysis.status = status
    analysis.progress_stage = status
    analysis.error_code = code.value
    analysis.error_message = message
    analysis.finished_at = utcnow()
    analysis.updated_at = utcnow()
    await db.flush()
    await db.refresh(analysis)
    return analysis

  async def list_expired_terminal_ids(self, db: AsyncSession, before: datetime) -> list[UUID]:
    result = await db.execute(
      select(Analysis.id).where(
        Analysis.expires_at < before,
        Analysis.status.in_([AnalysisStatus.COMPLETED, AnalysisStatus.FAILED, AnalysisStatus.TIMED_OUT]),
      )
    )
    return list(result.scalars().all())


analysis_repository = AnalysisRepository()
