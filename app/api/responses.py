from app.exceptions import BaseErrorResponse


COMMON_RESPONSES = {
  400: {"model": BaseErrorResponse},
  401: {"model": BaseErrorResponse},
  404: {"model": BaseErrorResponse},
  422: {"model": BaseErrorResponse},
  500: {"model": BaseErrorResponse},
}