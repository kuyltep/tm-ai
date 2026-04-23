import logging
import re
import shutil
from pathlib import Path
from uuid import UUID

from fastapi import UploadFile

from app.exceptions import ValidationAppError

logger = logging.getLogger("app.media")

MAX_FILE_SIZE_BYTES = 1_073_741_824
MAX_DURATION_SECONDS = 3 * 60 * 60
CHUNK_SIZE = 1024 * 1024
MEDIA_ROOT = Path("/tmp/talent-mind-analyses")

_ALLOWED_PREFIXES = ("audio/", "video/")
_SAFE_NAME_RE = re.compile(r"[^a-zA-Z0-9._-]+")


def validate_content_type(upload: UploadFile) -> str:
  content_type = upload.content_type or ""
  if not content_type.startswith(_ALLOWED_PREFIXES):
    raise ValidationAppError("Only audio/* and video/* files are supported")
  return content_type


def sanitize_filename(filename: str | None) -> str:
  value = filename or "upload.bin"
  safe = _SAFE_NAME_RE.sub("_", Path(value).name).strip("._")
  return safe or "upload.bin"


def analysis_dir(analysis_id: UUID) -> Path:
  return MEDIA_ROOT / str(analysis_id)


async def save_upload_file(upload: UploadFile, analysis_id: UUID) -> tuple[Path, int, str]:
  content_type = validate_content_type(upload)
  directory = analysis_dir(analysis_id)
  directory.mkdir(parents=True, exist_ok=True)
  target = directory / sanitize_filename(upload.filename)

  total = 0
  with target.open("wb") as destination:
    while chunk := await upload.read(CHUNK_SIZE):
      total += len(chunk)
      if total > MAX_FILE_SIZE_BYTES:
        cleanup_analysis_files(analysis_id)
        raise ValidationAppError("File size must be less than or equal to 1 GB")
      destination.write(chunk)

  await upload.close()
  return target, total, content_type


def cleanup_analysis_files(analysis_id: UUID) -> None:
  shutil.rmtree(analysis_dir(analysis_id), ignore_errors=True)


def cleanup_expired_paths(analysis_ids: list[UUID]) -> None:
  for analysis_id in analysis_ids:
    cleanup_analysis_files(analysis_id)
