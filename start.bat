@echo off
REM ===========================================================
REM  Website Builder - Unified Startup (Windows)
REM  Starts Flask backend (port 5050) + React frontend (port 3000)
REM  Each service opens in its own console window.
REM ===========================================================

cd /d "%~dp0"

set BACKEND_PORT=5050
set FRONTEND_PORT=3000

echo.
echo ==========================================================
echo          Website Builder - Unified Startup
echo          Flask backend + React frontend
echo ==========================================================
echo.

REM ---------- Pre-flight checks ----------
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

REM ---------- Backend setup ----------
echo.
echo [1/3] Setting up Flask backend...
cd flask-backend
if not exist "venv\Scripts\python.exe" (
    echo       Creating Python virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment.
        cd ..
        pause
        exit /b 1
    )
)

call "venv\Scripts\activate.bat"
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment.
    cd ..
    pause
    exit /b 1
)

echo       Installing Python dependencies...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install Python dependencies.
    cd ..
    pause
    exit /b 1
)

if not exist ".env" (
    if exist ".env.example" (
        copy /y .env.example .env >nul
    )
)

echo       Ensuring admin user exists...
python seed_admin.py >nul 2>&1

echo       OK - Backend ready
cd ..

REM ---------- Frontend setup ----------
echo.
echo [2/3] Setting up React frontend...
cd frontend
if not exist "node_modules" (
    echo       Installing npm packages ^(first run only, may take a few minutes^)...
    call npm install --silent --no-audit --no-fund
    if errorlevel 1 (
        echo [ERROR] Failed to install npm packages.
        cd ..
        pause
        exit /b 1
    )
)
echo       OK - Frontend ready
cd ..

REM ---------- Start both services in separate windows ----------
echo.
echo [3/3] Starting services...

start "Website Builder - BACKEND (port %BACKEND_PORT%)" cmd /k "cd /d %~dp0flask-backend && call venv\Scripts\activate.bat && set FLASK_RUN_PORT=%BACKEND_PORT% && python run.py"

timeout /t 3 /nobreak >nul

start "Website Builder - FRONTEND (port %FRONTEND_PORT%)" cmd /k "cd /d %~dp0frontend && set BROWSER=none&& set REACT_APP_BACKEND_URL=http://localhost:%BACKEND_PORT%&& npm start"

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
echo   To stop: close both console windows
echo.
echo ==========================================================
echo.
pause
