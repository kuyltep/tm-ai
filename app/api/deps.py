from fastapi.security import APIKeyHeader
from fastapi import Depends
from app.exceptions import UnauthorizedAppError
from app.settings import get_settings

from secrets import compare_digest

api_key_header = APIKeyHeader(name="Authorization", auto_error=True)


def check_api_key(api_key: str = Depends(api_key_header)) -> None:

  if not api_key:
    raise UnauthorizedAppError("Autrhorization not provided")
  settings = get_settings()
  expected = settings.api_key.get_secret_value()

  if not compare_digest(expected.strip(), api_key.strip()):
    raise UnauthorizedAppError("Invalid api key was provided")

  return
