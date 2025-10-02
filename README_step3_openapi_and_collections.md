# Step 3 — OpenAPI → коллекции (Postman / Bruno)

Что входит
----------
- `tools/generate_openapi.py` — берёт FastAPI-приложение (`app.main:app`) и сохраняет `collections/openapi.json`.
- `tools/make_postman.py` — собирает `collections/postman/Analog2CAD.postman_collection.json`.
- `tools/make_bruno.py` — собирает структуру для Bruno в `collections/bruno/Analog2CAD/...`.

Как использовать (Windows CMD)
------------------------------
1) Сгенерировать OpenAPI:
   ```
   .venv\Scripts\python tools\generate_openapi.py
   ```
2) Сделать Postman:
   ```
   .venv\Scripts\python tools\make_postman.py
   ```
   Импортируй `collections\postman\Analog2CAD.postman_collection.json` в Postman.
3) Сделать Bruno:
    ```
    .venv\Scripts\python tools\make_bruno.py
    ```
    В Bruno добавь папку `collections\bruno\Analog2CAD`.

Примечания
----------
- Скрипты читают примеры тел запросов из `requestBody.examples` или кладут `{}` для POST/PUT/PATCH.
- Переменные:
  - `baseUrl` (по умолчанию `http://127.0.0.1:8011`)
  - `token` (по умолчанию `demo`)
- После изменения API запусти скрипты ещё раз, чтобы обновить коллекции.
