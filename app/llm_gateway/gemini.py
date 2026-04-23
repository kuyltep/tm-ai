import base64
import logging
from pathlib import Path
from typing import Any

from langchain_core.exceptions import OutputParserException
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import ValidationError

from app.exceptions import ProviderAppError, SchemaAppError
from app.llm_gateway.schemas import InterviewAnalysisResponse
from app.settings import get_settings

logger = logging.getLogger("app.llm")

MODEL_SEQUENCE = [
  ("gemini-2.5-pro", 2),
  ("gemini-3.1-pro-preview", 1),
  ("gemini-3-flash-preview", 2),
]


def _load_prompt() -> str:
  prompt_path = Path("prompts/analyze.txt")
  if not prompt_path.exists():
    raise ProviderAppError("Prompt file not found")
  return prompt_path.read_text(encoding="utf-8").strip()


def _guess_mime_type(path: Path) -> str:
  suffix = path.suffix.lower()
  if suffix in {".mp3", ".mpeg"}:
    return "audio/mpeg"
  if suffix == ".wav":
    return "audio/wav"
  if suffix == ".m4a":
    return "audio/mp4"
  if suffix == ".ogg":
    return "audio/ogg"
  return "audio/mpeg"


def _build_structured_model(model_name: str):
  settings = get_settings()
  api_key = settings.google_api_key.get_secret_value()
  if not api_key:
    raise ProviderAppError("Google API key is not configured")

  llm = ChatGoogleGenerativeAI(
    model=model_name,
    google_api_key=api_key,
    temperature=0,
    max_output_tokens=14000,
  )
  return llm.with_structured_output(InterviewAnalysisResponse)


def _build_message(audio_path: Path) -> list[HumanMessage]:
  prompt = _load_prompt()
  encoded_audio = base64.b64encode(audio_path.read_bytes()).decode("ascii")
  return [
    HumanMessage(
      content=[
        {"type": "text", "text": prompt},
        {
          "type": "audio",
          "mime_type": _guess_mime_type(audio_path),
          "base64": encoded_audio,
        },
      ]
    )
  ]


async def _invoke_with_fallbacks(audio_path: Path) -> dict[str, Any]:

  primary_model, primary_retries = MODEL_SEQUENCE[0]
  primary = _build_structured_model(primary_model).with_retry(stop_after_attempt=primary_retries)

  fallback_models = [_build_structured_model(model_name) for model_name, _ in MODEL_SEQUENCE[1:]]
  chain = primary.with_fallbacks(fallback_models)

  message = _build_message(audio_path)
  response = await chain.ainvoke(message)
  return response.model_dump(mode="json")


async def analyze_audio_with_cascade(
  audio_path: Path,
  analysis_id: str,
) -> dict[str, Any]:
  try:
    result = await _invoke_with_fallbacks(audio_path)
    logger.info("llm pipeline succeeded", extra={"analysis_id": analysis_id})
    return result
  except (ValidationError, OutputParserException) as exc:
    raise SchemaAppError(str(exc)) from exc
  except SchemaAppError:
    raise
  except Exception as exc:
    message = getattr(exc, "message", str(exc))
    raise ProviderAppError(message) from exc
