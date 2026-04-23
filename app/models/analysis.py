from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from sqlalchemy import JSON, DateTime, Enum, Index, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.models.enums import AnalysisStatus
from app.db.database import Base


def utcnow() -> datetime:
  return datetime.now(timezone.utc)


def default_expires_at() -> datetime:
  return utcnow() + timedelta(days=7)


class Analysis(Base):
  __tablename__ = "analysis"

  id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
  user_id: Mapped[UUID | None] = mapped_column(Uuid, nullable=True, index=True)
  status: Mapped[AnalysisStatus] = mapped_column(
    Enum(
      AnalysisStatus,
      name="analysis_status",
      native_enum=False,
      values_callable=lambda enum_cls: [member.value for member in enum_cls],
    ),
    default=AnalysisStatus.QUEUED,
    nullable=False,
    index=True,
  )
  progress_stage: Mapped[AnalysisStatus] = mapped_column(
    Enum(
      AnalysisStatus,
      name="analysis_progress_stage",
      native_enum=False,
      values_callable=lambda enum_cls: [member.value for member in enum_cls],
    ),
    default=AnalysisStatus.QUEUED,
    nullable=False,
  )
  result: Mapped[dict | None] = mapped_column(JSON, nullable=True)
  error_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
  error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
  audio_name: Mapped[str] = mapped_column(String(512), nullable=False)
  idempotency_key: Mapped[str | None] = mapped_column(String(255), nullable=True)
  created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False, index=True)
  updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)
  started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
  finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
  expires_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True), default=default_expires_at, nullable=False, index=True
  )


Index(
  "ix_analysis_idempotency_key",
  Analysis.idempotency_key,
  unique=True,
  postgresql_where=Analysis.idempotency_key.is_not(None),
)
