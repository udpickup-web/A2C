# 01_DONE_CR_Core_API_v1.md

## TL;DR
Бэкенд переведён на **mobile-first** API `/api/v1`, выровнен под ТЗ, единый контракт ошибок, CORS, Bearer‑auth (prod), health, ENV/порт, Docker/Compose, автотесты (pytest), линт/формат (ruff/black), pre‑commit. Смоук пройден локально и в Docker.

---

## Что сделано

### API и маршруты (FastAPI, pydantic v2)
Префикс: `APIRouter(prefix="/api/v1")`.

**GET /api/v1/healthz** → `200 {"status":"ok"}`

**POST /api/v1/preflight**
- Вход: `preflight.schema.json`
- Выход: `normalized`, `preflight_id`

**POST /api/v1/views**
- Вход: `views.schema.json`
- Выход: агрегаты (`views_count`, `areas`, `solved_all`, `stats`)

**POST /api/v1/register**
- Вход: `{ "views": <views.json>, "preflight": <preflight.json> }`
- Выход: `{ "views_anchors": {...}, "views": <echo>, "preflight": <echo> }`
- Назначение: «согласование видов» (из 04_TZ)

**POST /api/v1/export**
- Вход: `features.schema.json` + `model_plan.schema.json` **или** (позже) `{ "model_id": "..." }`
- Текущий ответ (заглушки): `step_url`, `stl_url`, `glb_url`, `export_report`  
  Пример: `/artifacts/<uuid>/model.step`

**POST /api/v1/upload** (multipart)
- Старый загрузочный `/register` → переименован в `/upload`
- Вход: `file`
- Выход: `{ "upload_id","filename","size","url" }`

### Единый контракт ошибок
Всегда:
```json
{"error":{"code":<int>,"message":"<text>","details":{...}}}
```
- 400 — Empty JSON body (для `application/json`)
- 413 — Request body too large (лимит по ENV)
- 415 — Unsupported Media Type (middleware проверяет Content‑Type)
- 422 — Validation error (pydantic v2), `details` — список ошибок
- 500 — Internal server error (fallback)

В ответах добавляется `X-Request-Id` (корреляция).

### Аутентификация
- **prod**: Bearer‑токен обязателен (`Authorization: Bearer <TOKEN>`). Если `AUTH_TOKEN` не задан — принимается любой токен.
- **dev**: токен опционален (`AUTH_REQUIRED=0`).
- Поддерживаем заголовок `X-Request-Id` (если пришёл — прокидываем).

### CORS
- **dev**: `*`
- **prod**: whitelist из `CORS_ORIGINS` (CSV в ENV).

### ENV / порт / лимиты
- `PORT` (по умолчанию **8011**)
- `APP_ENV` (`dev`/`prod`)
- `AUTH_REQUIRED=0/1`, `AUTH_TOKEN=<строка>`
- `CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000`
- `MAX_BODY_MB=10` → 413

### Docker / Compose
**Dockerfile**: `python:3.12-slim`, `uvicorn app.main:app --host 0.0.0.0 --port 8011`  
**docker-compose.yml**: сервис `coreapi`, порты `8011:8011`, ENV, том `./artifacts:/app/artifacts`.

### Батники
- `win/run_dev.bat` — RELOAD‑тумблер (`RELOAD=0/1`, по умолчанию 1)
- `win/run_prod.bat` — без reload, `0.0.0.0`

### Тесты (pytest)
`tests/`:
- `test_health.py` — `/healthz`
- `test_preflight.py` — happy‑path + лишние поля → 422 + error‑формат
- `test_register_export.py` — `/register` → anchors; `/export` → ссылки
- `test_errors.py` — пустой JSON → 400, недостающие поля → 422

**Факт:** локально 6 passed. Ручные проверки: 400/415/422/413 — **ОК**.

### OpenAPI
`scripts/generate_openapi.py` — генерит `openapi.json` (fixed under ruff).

### Pre‑commit / стиль
- `.pre-commit-config.yaml` — `ruff` (lint+format) + `black`
- `pyproject.toml` — target py311 (можно менять)
- `.gitattributes` — нормализация окончаний строк

### CI (готов файл)
- `.github/workflows/ci.yml` — pytest (+ docker build джоба). Версию Python можно сделать матричной.

---

## Как запускать

### Dev (venv)
```
win\run_dev.bat
# либо
uvicorn app.main:app --host 127.0.0.1 --port 8011
```

### Prod (Docker)
```
docker compose up --build -d
curl.exe -H "Authorization: Bearer demo" http://127.0.0.1:8011/api/v1/healthz
```

### Примеры запросов
```
# preflight
curl.exe -H "Authorization: Bearer demo" -H "Content-Type: application/json" --data-binary "@samples\preflight.sample.json" http://127.0.0.1:8011/api/v1/preflight

# register
curl.exe -H "Authorization: Bearer demo" -H "Content-Type: application/json" --data-binary "@samples\register.sample.json" http://127.0.0.1:8011/api/v1/register

# export
curl.exe -H "Authorization: Bearer demo" -H "Content-Type: application/json" --data-binary "@samples\export_by_features.sample.json" http://127.0.0.1:8011/api/v1/export

# upload (multipart)
curl.exe -H "Authorization: Bearer demo" -F "file=@samples\preflight.sample.json" http://127.0.0.1:8011/api/v1/upload
```

### Негативка (контракт ошибок)
```
# 400
iwr -Method POST -Uri http://127.0.0.1:8011/api/v1/preflight -Headers @{Authorization='Bearer demo'} -ContentType 'application/json' -Body '' -Verbose

# 415
curl.exe -H "Authorization: Bearer demo" -H "Content-Type: text/plain" --data "foo" http://127.0.0.1:8011/api/v1/preflight -v

# 422
iwr -Method POST -Uri http://127.0.0.1:8011/api/v1/preflight -Headers @{Authorization='Bearer demo'} -ContentType 'application/json' -Body '{"standard":"ISO"}' -Verbose

# 413 (11MB)
fsutil file createnew .\big.bin 11534336
$abs = (Resolve-Path .\big.bin).Path
curl.exe -H "Authorization: Bearer demo" -H "Content-Type: application/json" --data-binary "@$abs" http://127.0.0.1:8011/api/v1/preflight -v
```
