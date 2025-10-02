# Core API (TZ v1) — mobile-first

FastAPI-бэкенд под мобильный клиент. Версия API: **/api/v1** (APIRouter prefix).

## Быстрый старт (Windows, Python 3.11)

```bat
win\create_venv.bat
win\run_dev.bat
```

Открыть Swagger UI: http://127.0.0.1:8011/docs  
Проверка здоровья: GET http://127.0.0.1:8011/api/v1/healthz

Сохранить OpenAPI:
```bat
win\generate_openapi.bat
```

## ENV
- `PORT` — порт uvicorn (по умолчанию 8011).
- `APP_ENV` — `dev` (по умолчанию) или `prod`.
- `CORS_ORIGINS` — список через запятую (используется в `prod`). В `dev` CORS=\*.
- `AUTH_REQUIRED` — `1` чтобы требовать Bearer-токен (в `dev` по умолчанию выключено).
- `AUTH_TOKEN` — допустимый Bearer-токен при `AUTH_REQUIRED=1`.
- `MAX_BODY_MB` — лимит тела запроса в MB (по умолчанию 10).

## Контракты и маршруты
- Префикс: **`/api/v1`**
- **GET `/api/v1/healthz`** → `{"status":"ok"}`
- **POST `/api/v1/preflight`**
- **POST `/api/v1/views`**
- **POST `/api/v1/sketch2d`**
- **POST `/api/v1/plan`**
- **POST `/api/v1/build`**
- **POST `/api/v1/register`** — согласование видов: вход `{"views":..., "preflight":...}`; выход `{"views_anchors":..., "views":...}`
- **POST `/api/v1/export`** — вход: `{"model_id": "..."}` **или** `{"features":..., "plan":...}`; выход: ссылки `step_url|stl_url|glb_url` + `export_report`
- **POST `/api/v1/upload`** — multipart upload (если нужно грузить файлы отдельно)

Статика артефактов: монтируется на `/artifacts/<id>/<file>` (локальные ссылки).

## Единый контракт ошибок
На 400/413/415/422/500 сервер отвечает:
```json
{ "error": { "code": <int>, "message": "<text>", "details": {} } }
```
Заголовки: `Authorization: Bearer <token>` (опционально в dev), `X-Request-Id` (при отсутствии генерируется).

## Примеры (PowerShell)
```powershell
# health
curl http://127.0.0.1:8011/api/v1/healthz

# preflight
curl -Method POST -Uri http://127.0.0.1:8011/api/v1/preflight -ContentType "application/json" -InFile samples/preflight.sample.json

# views
curl -Method POST -Uri http://127.0.0.1:8011/api/v1/views -ContentType "application/json" -InFile samples/views.sample.json

# register (views + preflight)
curl -Method POST -Uri http://127.0.0.1:8011/api/v1/register -ContentType "application/json" -InFile samples/register.sample.json

# export (features + plan)
curl -Method POST -Uri http://127.0.0.1:8011/api/v1/export -ContentType "application/json" -InFile samples/export_by_features.sample.json
```
