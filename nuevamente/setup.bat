@echo off
cd /d "%~dp0"
python -m venv .venv
call .venv\Scripts\activate
pip install -r backend\requirements.txt
echo.
echo Instalacion terminada. Ahora abre run_api.bat y run_ui.bat.
pause
