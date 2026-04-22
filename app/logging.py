import contextvars
import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any

request_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar("request_id", default=None)


class JsonFormatter(logging.Formatter):
  def format(self, record: logging.LogRecord) -> str:
    payload: dict[str, Any] = {
      "timestamp": datetime.now(timezone.utc).isoformat(),
      "level": record.levelname.lower(),
      "logger": record.name,
      "message": record.getMessage(),
    }
    request_id = getattr(record, "request_id", None) or request_id_var.get()
    if request_id:
      payload["request_id"] = request_id
    for key in ("method", "path", "status_code", "latency_ms", "analysis_id", "stage", "model", "latency"):
      value = getattr(record, key, None)
      if value is not None:
        payload[key] = value
    if record.exc_info:
      payload["exc_info"] = self.formatException(record.exc_info)
    return json.dumps(payload, ensure_ascii=False)


def configure_logging(level: str) -> None:
  root = logging.getLogger()
  root.handlers.clear()
  handler = logging.StreamHandler(sys.stdout)
  handler.setFormatter(JsonFormatter())
  root.addHandler(handler)
  root.setLevel(level)
