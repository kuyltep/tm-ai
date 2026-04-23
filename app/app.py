from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError

from app.api.health import router as health_router
from app.api.v1.analyze.router import router as analysis_router
from app.handlers import app_exception_handler, http_exception_handler, validation_exception_handler
from app.exceptions import AppError
from app.middlewares import add_cors_middleware, RequestIdMiddleware
from app.logging import configure_logging
from app.settings import get_settings
from app.utils.lifespan import lifespan


def app() -> FastAPI:
  settings = get_settings()
  configure_logging(settings.log_level)

  application = FastAPI(title="TalentMind AI API", version="0.1.0", lifespan=lifespan)
  add_cors_middleware(application, settings)
  # application.add_middleware(ApiKeyMiddleware)
  application.add_middleware(RequestIdMiddleware)

  application.include_router(health_router)
  application.include_router(analysis_router)

  application.add_exception_handler(RequestValidationError, validation_exception_handler)
  application.add_exception_handler(HTTPException, http_exception_handler)
  application.add_exception_handler(AppError, app_exception_handler)

  return application
