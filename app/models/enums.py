from enum import StrEnum

class AnalysisStatus(StrEnum):
  QUEUED = "queued"
  PREPROCESSING = "preprocessing"
  RUNNING = "running"
  COMPLETED = "completed"
  FAILED = "failed"
  TIMED_OUT = "timed_out"

class AnalysisErrorCode(StrEnum):
  UNAUTHORIZED_ERROR = "unauthorized_error"
  NOT_FOUND_ERROR = "not_found_error"
  VALIDATION_ERROR = "validation_error"
  CONVERSION_ERROR = "conversion_error"
  PROVIDER_ERROR = "provider_error"
  SCHEMA_ERROR = "schema_error"
  TIMEOUT = "timeout"
  INTERNAL_ERROR = "internal_error"
