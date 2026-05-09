@echo off
REM ─────────────────────────────────────────────────────────────────────────
REM Website Builder — One-command startup script (Windows)
REM Starts BOTH the Flask backend and the React frontend together.
REM ─────────────────────────────────────────────────────────────────────────

setlocal enabledelayedexpansion
cd /d "%~dp0"

echo ==========================================================
echo          Website Builder - Starting up...
echo ==========================================================

REM --- Backend setup ---
echo.
echo [1/3] Setting up Flask backend...
cd flask-backend
if not exist "venv" (
    echo     Creating virtual environment...
    python -m venv venv
)
call venv\Scripts\activate.bat
pip install -q -r ..\requirements.txt
echo     OK - Backend dependencies ready

REM --- Frontend setup ---
echo.
echo [2/3] Setting up React frontend...
cd ..\frontend
if not exist "node_modules" (
    echo     Installing npm packages (this may take a moment)...
    call npm install --silent
)
echo     OK - Frontend dependencies ready

REM --- Start both services ---
echo.
echo [3/3] Starting services...
cd ..

start "Website Builder Backend" cmd /k "cd flask-backend && venv\Scripts\activate.bat && python run.py"
timeout /t 3 /nobreak >nul
start "Website Builder Frontend" cmd /k "cd frontend && set BROWSER=none && npm start"

echo.
echo ==========================================================
echo                      READY
echo ==========================================================
echo.
echo   OPEN THIS IN YOUR BROWSER:
echo.
echo       http://localhost:3000
echo.
echo   (The backend API lives at http://localhost:5000)
echo.
echo   Admin login:  admin@websitebuilder.com / Admin@1234
echo.
echo ==========================================================
echo.
pause
