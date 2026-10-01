@echo off
cd /d "%~dp0"
python -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)" || ( echo Se necesita Python 3.11 o superior. & pause & exit /b 1 )
python -m venv .venv
call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r backend\requirements.txt
echo.
echo Instalacion terminada. Ahora abre run_api.bat
pause
