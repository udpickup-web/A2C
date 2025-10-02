# 02_TODO_CR_Core_API_v1.md

## Следующие шаги (приоритет)

### 1) /export по `model_id` (добавить альтернативный вход)
- Поддержать `{ "model_id": "<id>" }` как альтернативу `features+plan`.
- Валидация `model_id` (UUID/ULID — выбрать формат).
- Ответ тот же: `step_url`, `stl_url`, `glb_url`, `export_report`.
- Временный резолвер: `artifacts/<model_id>/model.*` (заглушка).

### 2) CORS в prod
- Перечень доменов фронта в `CORS_ORIGINS` (CSV). Проверить, что в Docker действительно whitelist, а не `*`.

### 3) OpenAPI → коллекция
- `python scripts/generate_openapi.py` → `openapi.json` в корне.
- Импортировать в Postman/Insomnia, положить `.json` коллекции в `/docs/` или `/postman/`.

### 4) CI
- При необходимости — матрица Python (3.11/3.13).
- Отдельный workflow на docker build & push (Docker Hub или GHCR) — потребуются секреты.

### 5) Prod‑укрепление
- `Dockerfile`:
  - `HEALTHCHECK CMD curl -f http://localhost:8011/api/v1/healthz || exit 1`
  - non‑root user.
- Uvicorn:
  - опционально `--workers N` для CPU>2, `--proxy-headers` за ingress.
- Логи:
  - JSON‑логи со связкой `X-Request-Id`.

### 6) Лимиты/валидация
- Уже есть: 413 (MAX_BODY_MB), 415 (Content‑Type), 422 (extra='forbid'), 400 (empty JSON).
- Добавить: лимит multipart размера на `/upload` (если нужно).

### 7) Чистовые
- `README.md` (команды запуска, ENV, curl‑примеры).
- `CHANGELOG.md` (зафиксировать CR).
- Postman/Insomnia коллекция.

### 8) Тесты
- Добить негативные кейсы для `features.schema.json` / `model_plan.schema.json` (лишние поля → 422).
- Юнит на `/export` с `model_id` и happy‑path ссылками.

---

## Шпаргалка по окружению

**ENV пример (`.env.example`):**
```
PORT=8011
APP_ENV=dev
AUTH_REQUIRED=0
AUTH_TOKEN=change-me
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
MAX_BODY_MB=10
```

**Docker compose (prod‑профиль):**
```yaml
services:
  coreapi:
    build: .
    ports:
      - "8011:8011"
    environment:
      - APP_ENV=prod
      - AUTH_REQUIRED=1
      - CORS_ORIGINS=https://your-mobile.app
      # - AUTH_TOKEN=supersecret123   # задать при необходимости
    volumes:
      - ./artifacts:/app/artifacts
    restart: unless-stopped
```

**Авторизация:**
- prod → обязательно `Authorization: Bearer <token>`
- dev → опционально (или включаем `AUTH_REQUIRED=1`)

**Артефакты:**
- Ссылки из /export работают локально как `/artifacts/<id>/model.step`.

---

## Что говорить в новом чате
> «Есть два файла в корне проекта: **01_DONE_CR_Core_API_v1.md** и **02_TODO_CR_Core_API_v1.md**. Продолжаем со второй части (TODO): реализуем `/export` по `model_id`, готовим Postman коллекцию и настраиваем CI под docker push.»
