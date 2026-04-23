import logging
import time
from uuid import uuid4

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.logging import request_id_var

logger = logging.getLogger("app.request")


class RequestIdMiddleware(BaseHTTPMiddleware):
  async def dispatch(self, request: Request, call_next) -> Response:
    request_id = request.headers.get("X-Request-ID") or str(uuid4())
    token = request_id_var.set(request_id)
    request.state.request_id = request_id
    start = time.perf_counter()
    try:
      response = await call_next(request)
    except Exception:
      latency_ms = round((time.perf_counter() - start) * 1000, 2)
      logger.exception(
        "request failed",
        extra={
          "request_id": request_id,
          "method": request.method,
          "path": request.url.path,
          "latency_ms": latency_ms,
        },
      )
      raise
    finally:
      request_id_var.reset(token)
    latency_ms = round((time.perf_counter() - start) * 1000, 2)
    response.headers["X-Request-ID"] = request_id
    logger.info(
      "request completed",
      extra={
        "request_id": request_id,
        "method": request.method,
        "path": request.url.path,
        "status_code": response.status_code,
        "latency_ms": latency_ms,
      },
    )
    return response
