@echo off
setlocal
cd /d %~dp0\..
if not exist .venv\Scripts\activate (
  echo [ERROR] VENV not found. Run win\create_venv.bat first.
  exit /b 1
)
call .venv\Scripts\activate
python -m pip install -U pip
pip install -r requirements.txt
pip install pytest httpx
pytest -q
