# Step 2 — CORS в проде (строгий whitelist)

Что добавлено
-------------
- `.env.prod.example` — шаблон переменных окружения:
  - `APP_ENV=prod` включает строгий режим.
  - `AUTH_REQUIRED=1` (и/или `APP_ENV=prod`) включает обязательный Bearer.
  - `CORS_ORIGINS` — CSV без пробелов (перечислить домены).
- `docker-compose.prod.yml` — профиль прод-сервиса, монтирует `./artifacts`, публикует `8011`.
- `tests/test_cors_prod.py` — проверка, что в prod отражается только whitelisted origin.

Как включить
------------
1. Скопируй `.env.prod.example` в `.env.prod` и заполни:
   ```ini
   APP_ENV=prod
   AUTH_REQUIRED=1
   AUTH_TOKEN=<секрет>
   CORS_ORIGINS=https://analog2cad.com,https://app.analog2cad.com
   ```
2. Собери и подними prod:
   ```bat
   docker compose -f docker-compose.prod.yml build --no-cache
   docker compose -f docker-compose.prod.yml up -d
   ```
3. Проверка:
   ```bat
   set ORIGIN=https://analog2cad.com
   "%SystemRoot%\System32\curl.exe" -X OPTIONS -H "Origin: %ORIGIN%" -H "Access-Control-Request-Method: POST" http://127.0.0.1:8011/api/v1/healthz -i
   ```
   В заголовках ответа должно быть `access-control-allow-origin: %ORIGIN%`.
   Для чужого домена заголовок должен отсутствовать или быть `null`.
