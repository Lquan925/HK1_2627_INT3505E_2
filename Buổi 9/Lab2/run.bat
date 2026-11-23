@echo off
setlocal
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" goto install
where py >nul 2>nul
if not errorlevel 1 (
    py -3 -m venv .venv
) else (
    python -m venv .venv
)
if errorlevel 1 goto failed
:install
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto failed
echo Open http://127.0.0.1:5000/users/1 in your browser.
".venv\Scripts\python.exe" app.py
pause
exit /b
:failed
echo Setup failed. Install Python 3.10 or newer and enable Add Python to PATH.
pause
exit /b 1
