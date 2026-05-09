@echo off
REM ─────────────────────────────────────────────────────────────────────────
REM Website Builder — One-command startup (Windows)
REM
REM Starts BOTH the Flask backend (port 5000) and the React frontend (3000)
REM together. Each service opens in its own console window.
REM ─────────────────────────────────────────────────────────────────────────

setlocal enabledelayedexpansion
cd /d "%~dp0"

set BACKEND_PORT=5000
set FRONTEND_PORT=3000

echo.
echo ==========================================================
echo          Website Builder - Unified Startup
echo          Flask backend + React frontend
echo ==========================================================
echo.

REM --- Pre-flight checks ---
where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not on PATH.
    pause
    exit /b 1
)

where node >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed or not on PATH.
    pause
    exit /b 1
)

REM --- Port conflict detection ---
call :check_port %BACKEND_PORT%  Backend
call :check_port %FRONTEND_PORT% Frontend

REM --- Backend setup ---
echo.
echo [1/3] Setting up Flask backend...
cd flask-backend
if not exist "venv" (
    echo       Creating Python virtual environment...
    python -m venv venv
)
call venv\Scripts\activate.bat
pip install -q -r ..\requirements.txt
if not exist ".env" (
    if exist ".env.example" (
        copy /y .env.example .env >nul
    )
)
echo       OK - Backend ready
cd ..

REM --- Frontend setup ---
echo.
echo [2/3] Setting up React frontend...
cd frontend
if not exist "node_modules" (
    echo       Installing npm packages (first run only, may take a few minutes)...
    call npm install --silent --no-audit --no-fund
)
echo       OK - Frontend ready
cd ..

REM --- Start both services in separate windows ---
echo.
echo [3/3] Starting services...
start "Website Builder - BACKEND (port %BACKEND_PORT%)"  cmd /k "cd flask-backend && call venv\Scripts\activate.bat && python run.py"
timeout /t 3 /nobreak >nul
start "Website Builder - FRONTEND (port %FRONTEND_PORT%)" cmd /k "cd frontend && set BROWSER=none&& npm start"

echo.
echo ==========================================================
echo                       READY
echo ==========================================================
echo.
echo   OPEN IN YOUR BROWSER:
echo.
echo       http://localhost:%FRONTEND_PORT%
echo.
echo   Backend API:  http://localhost:%BACKEND_PORT%/api/health
echo   Admin login:  admin@websitebuilder.com / Admin@1234
echo.
echo   To stop: close both console windows or run "npm run stop"
echo.
echo ==========================================================
echo.
pause
goto :eof

REM ──────────────────────────────────────────────────────────
:check_port
set _port=%~1
set _name=%~2
netstat -an | findstr /C:":%_port% " | findstr /C:"LISTENING" >nul
if not errorlevel 1 (
    echo [WARN] Port %_port% ^(%_name%^) is already in use.
    set /p _ans="       Kill the process and continue? (y/N): "
    if /i "!_ans!"=="y" (
        for /f "tokens=5" %%p in ('netstat -ano ^| findstr /C:":%_port% " ^| findstr /C:"LISTENING"') do (
            taskkill /F /PID %%p >nul 2>&1
        )
        echo       Port %_port% freed.
    ) else (
        echo [ERROR] Aborting. Free port %_port% and try again.
        pause
        exit /b 1
    )
)
goto :eof
