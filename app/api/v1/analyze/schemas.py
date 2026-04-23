from datetime import datetime
from app.models.enums import AnalysisStatus, AnalysisErrorCode
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AnalysisError(BaseModel):
  code: AnalysisErrorCode
  message: str


class CreateAnalysisResponse(BaseModel):
  analysis_id: UUID
  status: AnalysisStatus


class AnalysisResponse(BaseModel):
  id: UUID | None = None
  user_id: UUID | None = None
  status: AnalysisStatus
  progress_stage: AnalysisStatus
  result: dict[str, Any] | None = None
  error: AnalysisError | None = None
  audio_name: str | None = None
  created_at: datetime | None = None
  updated_at: datetime | None = None
  started_at: datetime | None = None
  finished_at: datetime | None = None
  expires_at: datetime | None = None


class AnalysisOutputSchema(BaseModel):
  """Placeholder for the final LangChain structured output.

  Replace this model's fields with the final report schema when the format is ready.
  Keeping `extra="allow"` lets v1 validate that the model returns an object while
  avoiding premature constraints on the report shape.
  """

  model_config = ConfigDict(extra="allow")
