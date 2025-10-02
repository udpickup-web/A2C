# Step 1 — /export by model_id

Что сделано
-----------
- Обновлённый `app/routers/export.py`:
  - Поддерживает альтернативный вход `{ "model_id": "<uuid>" }`.
  - Возвращает ссылки `/artifacts/<uuid>/model.{step,stl,glb}` и `export_report` с полем `exists`.
  - Сценарий через `{ "features": {...}, "model_plan": {...} }` сохранён как заглушка — генерит новый UUID.

Как внедрить
------------
1. Заменить файл `app/routers/export.py` на версию из этого архива.
2. Убедиться, что в `app/main.py` этот роутер подключён (как и раньше), например:
   ```python
   from app.routers import export as export_router
   app.include_router(export_router.router)
   ```
3. (Необязательно) Положить тест `tests/test_export_model_id.py` и прогнать `pytest`.
4. (Необязательно) Для ручной проверки:
   ```bat
   curl.exe -H "Authorization: Bearer demo" -H "Content-Type: application/json" --data-binary "@samples\export_by_id.sample.json" http://127.0.0.1:8011/api/v1/export
   ```

Примечания
----------
- Каталог артефактов монтируется как `./artifacts:/app/artifacts` (см. docker-compose).
- В dev окружении токен опционален, в prod — обязателен.
- Контракт ошибок остаётся единым и формируется глобальными middleware/handlers проекта.
