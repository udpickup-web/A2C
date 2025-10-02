# 06_TZ_CAD_Builder — CAD‑Builder (CadQuery/Build123d/OCC)
Версия: 1.0 • Дата: 2025-10-02

## Цель
- Построить 3D по features/plan с устойчивостью.

## Вход
- `features.json`, `model_plan.json`.

## Выход
- Твердотельная модель + отчёт.

## Алгоритм/требования к реализации
- Реализовать операции extrude/revolve add/cut, array/mirror, shell, hole, chamfer, fillet; безопасные ссылки.

## API/Интерфейсы
- `POST /build` и CLI.

## Критерии приёмки
- Открывается в FreeCAD/SW; совпадение ключевых размеров.

## Артефакты
- `build_report.json`, сечения для валидации.

## Примечания
