from pathlib import Path
from uuid import UUID
import httpx

from app.exceptions import ConversionAppError
from app.settings import get_settings
from app.media.utils import analysis_dir


async def convert_video_to_audio(path: Path, analysis_id: UUID) -> Path:
  settings = get_settings()
  output = analysis_dir(analysis_id) / "converted-audio.mp3"
  headers = {"X-API-Key": settings.converter_api_key.get_secret_value()}
  try:
    async with httpx.AsyncClient(timeout=60000) as client:
      with path.open("rb") as file_obj:
        response = await client.post(
          settings.converter_url,
          headers=headers,
          files={"file": (path.name, file_obj, "video/mp4")},
        )
    response.raise_for_status()
  except httpx.HTTPError as exc:
    raise ConversionAppError(f"Video conversion failed: {exc}") from exc

  output.write_bytes(response.content)
  return output
