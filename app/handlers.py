from fastapi import Request, HTTPException
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse
from app.exceptions import ErrorDetail, BaseErrorResponse, AppError


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
  content = BaseErrorResponse(
    error=ErrorDetail(code="validation_error", message="Request validation failed", details=exc.errors())
  ).model_dump(exclude_none=True)
  return JSONResponse(status_code=422, content=content)


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
  detail = exc.detail
  if isinstance(detail, dict) and "code" in detail:
    error_detail = ErrorDetail(**detail)
  else:
    error_detail = ErrorDetail(code="http_error", message=str(detail))

  content = BaseErrorResponse(error=error_detail).model_dump(exclude_none=True)
  return JSONResponse(status_code=exc.status_code, content=content, headers=getattr(exc, "headers", None))


async def app_exception_handler(request: Request, exc: AppError) -> JSONResponse:
  content = BaseErrorResponse(
    error=ErrorDetail(
      code=exc.error_code.value if hasattr(exc.error_code, "value") else str(exc.error_code), message=exc.message
    )
  ).model_dump(exclude_none=True)
  return JSONResponse(status_code=exc.status_code, content=content)
