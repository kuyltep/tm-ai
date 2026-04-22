import uvicorn

from app.app import app
from app.settings import get_settings

application = app()


def main() -> None:
  settings = get_settings()
  uvicorn.run("main:application", host=settings.host, port=settings.port, reload=False)


if __name__ == "__main__":
  main()
