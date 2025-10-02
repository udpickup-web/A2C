from fastapi.testclient import TestClient
from app.main import app
import json
from pathlib import Path


def main():
    # Запускаем приложение, чтобы сработали startup-ивенты (если есть)
    with TestClient(app):
        pass
    # Генерим openapi.json
    openapi = app.openapi()
    Path("openapi.json").write_text(
        json.dumps(openapi, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
