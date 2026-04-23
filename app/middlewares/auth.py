from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from starlette.responses import JSONResponse
from starlette.responses import Response

from app.exceptions import BaseErrorResponse, ErrorDetail
from app.settings import get_settings
from secrets import compare_digest


class ApiKeyMiddleware(BaseHTTPMiddleware):
  async def dispatch(self, request: Request, call_next) -> Response:
    if request.url.path.startswith("/analyses"):
      settings = get_settings()
      expected = settings.api_key.get_secret_value()
      actual = request.headers.get("Authorization", "")
      if not expected or not actual or not compare_digest(actual, expected):
        content = BaseErrorResponse(error=ErrorDetail(code="unauthorized", message="Invalid API key")).model_dump(
          exclude_none=True
        )
        return JSONResponse(
          status_code=401,
          content=content,
        )
    return await call_next(request)
