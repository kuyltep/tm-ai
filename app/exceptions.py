from pydantic import BaseModel, Field
from typing import Any

from app.api.v1.analyze.schemas import AnalysisErrorCode


class ErrorDetail(BaseModel):
    code: str = Field(..., description="Error code identifier")
    message: str = Field(..., description="Human-readable error message")
    details: Any | None = Field(default=None, description="Additional error details")

class BaseErrorResponse(BaseModel):
    error: ErrorDetail


class AppError(Exception):
  status_code = 500
  error_code = AnalysisErrorCode.INTERNAL_ERROR

  def __init__(self, message: str):
    self.message = message
    super().__init__(message)


class ValidationAppError(AppError):
  status_code = 400
  error_code = AnalysisErrorCode.VALIDATION_ERROR


class UnauthorizedAppError(AppError):
  status_code = 401
  error_code = AnalysisErrorCode.UNAUTHORIZED_ERROR


class NotFoundAppError(AppError):
  status_code = 404
  error_code = AnalysisErrorCode.NOT_FOUND_ERROR


class ConversionAppError(AppError):
  error_code = AnalysisErrorCode.CONVERSION_ERROR


class ProviderAppError(AppError):
  error_code = AnalysisErrorCode.PROVIDER_ERROR


class SchemaAppError(AppError):
  error_code = AnalysisErrorCode.SCHEMA_ERROR


class TimeoutAppError(AppError):
  error_code = AnalysisErrorCode.TIMEOUT
