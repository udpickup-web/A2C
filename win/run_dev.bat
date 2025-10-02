@echo off
setlocal
cd /d %~dp0\..
if "%PORT%"=="" set PORT=8011
if "%RELOAD%"=="" set RELOAD=1
set APP_ENV=dev
if not exist .venv\Scripts\activate (
  echo [ERROR] VENV not found. Run win\create_venv.bat first.
  exit /b 1
)
call .venv\Scripts\activate
set RELOAD_FLAG=--reload
if "%RELOAD%"=="0" set RELOAD_FLAG=
uvicorn app.main:app --host 127.0.0.1 --port %PORT% %RELOAD_FLAG%
