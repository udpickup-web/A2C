from fastapi.testclient import TestClient
from app.main import app
import json, os

def main():
    # Создаем клиент, чтобы убедиться, что приложение поднимается
    client = TestClient(app)
    # Пишем OpenAPI в файл в корне
    openapi = app.openapi()
    with open("openapi.json", "w", encoding="utf-8") as f:
        json.dump(openapi, f, ensure_ascii=False, indent=2)
    print("[OK] openapi.json сохранён")

if __name__ == "__main__":
    main()
