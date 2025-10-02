@echo off
setlocal
cd /d %~dp0\..
where python >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Python не найден. Установи Python 3.11 и добавь в PATH.
  exit /b 1
)
python -m venv .venv
call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
echo [OK] VENV готов.
