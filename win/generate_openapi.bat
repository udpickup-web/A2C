@echo off
setlocal
cd /d %~dp0\..
if not exist .venv\Scripts\activate (
  echo [ERROR] VENV не найден. Сначала запусти win\create_venv.bat
  exit /b 1
)
call .venv\Scripts\activate
python scripts\generate_openapi.py
