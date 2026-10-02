@echo off
cd /d "%~dp0"
if not exist .venv ( echo Primero ejecuta setup.bat & pause & exit /b 1 )
call .venv\Scripts\activate
python -m streamlit run ui\app.py
pause
