@echo off
cd /d "%~dp0"
if not exist .venv ( echo Primero ejecuta setup.bat & pause & exit /b 1 )
call .venv\Scripts\activate
cd backend
python -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000
pause
