# Step 1 — /export по model_id (патч для single-file main.py)

Что изменено
------------
- Обновлён `app/main.py`: обработчик `/export` теперь поддерживает **взаимоисключающие** ветки:
  - `{"model_id":"<uuid>"}` → возврат ссылок `/artifacts/<id>/model.*` и `export_report.exists` без создания файлов.
  - `{"features":{...}, "plan":{...}}` → как раньше, **stub**: создаётся новый `export_id` и три файла-заглушки.
- Добавлены тесты `tests/test_export_model_id.py` (happy-path, смешанный ввод → 422, неверная форма → 400/422).
- Пример тела запроса: `samples/export_by_id.sample.json`.

Как внедрить
------------
1. Заменить **app/main.py** на версию из этого архива.
2. Запустить тесты:
   ```bash
   pytest -q
   ```
3. Ручная проверка:
   ```bat
   curl.exe -H "Authorization: Bearer demo" -H "Content-Type: application/json" --data-binary "@samples\export_by_id.sample.json" http://127.0.0.1:8011/api/v1/export
   ```

Заметки по CORS (шаг 2 TODO)
----------------------------
- В prod `allow_origins` берётся из `CORS_ORIGINS` (CSV), в dev — `*`. Проверь значения в docker-compose prod‑профиля.
