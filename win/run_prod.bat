@echo off
setlocal
cd /d %~dp0\..
if "%PORT%"=="" set PORT=8011
set APP_ENV=prod
if not exist .venv\Scripts\activate (
  echo [ERROR] VENV not found. Run win\create_venv.bat first.
  exit /b 1
)
call .venv\Scripts\activate
uvicorn app.main:app --host 0.0.0.0 --port %PORT%
