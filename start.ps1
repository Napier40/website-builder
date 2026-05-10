# ===========================================================
#  Website Builder - Unified Startup (Windows PowerShell)
#  Starts Flask backend (port 5050) + React frontend (port 3000)
#  Each service opens in its own PowerShell window.
# ===========================================================
#
#  Usage (from the project root):
#      powershell -ExecutionPolicy Bypass -File .\start.ps1
#
#  Or right-click start.ps1 -> "Run with PowerShell".
# ===========================================================

$ErrorActionPreference = 'Stop'

$ScriptDir     = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendDir    = Join-Path $ScriptDir 'flask-backend'
$FrontendDir   = Join-Path $ScriptDir 'frontend'
$BackendPort   = 5050
$FrontendPort  = 3000

function Write-Header([string]$Text) {
    Write-Host ''
    Write-Host '==========================================================' -ForegroundColor Cyan
    Write-Host "         $Text" -ForegroundColor Cyan
    Write-Host '==========================================================' -ForegroundColor Cyan
    Write-Host ''
}

function Write-Step([string]$Text) {
    Write-Host ''
    Write-Host "==> $Text" -ForegroundColor Yellow
}

function Write-Ok([string]$Text) {
    Write-Host "    OK - $Text" -ForegroundColor Green
}

function Write-Fail([string]$Text) {
    Write-Host "    ERROR - $Text" -ForegroundColor Red
}

function Test-Command([string]$Name) {
    $null = Get-Command $Name -ErrorAction SilentlyContinue
    return $?
}

Write-Header 'Website Builder - Unified Startup'
Write-Host "  Project root: $ScriptDir" -ForegroundColor Gray
Write-Host "  Backend:      port $BackendPort" -ForegroundColor Gray
Write-Host "  Frontend:     port $FrontendPort" -ForegroundColor Gray

# ---------- Pre-flight checks ----------
Write-Step 'Pre-flight checks'

if (-not (Test-Command 'python')) {
    Write-Fail 'Python is not installed or not on PATH.'
    Write-Host '    Install Python 3.9+ from https://www.python.org/downloads/' -ForegroundColor Yellow
    Read-Host 'Press Enter to exit'
    exit 1
}
Write-Ok ("Python found: " + (python --version))

if (-not (Test-Command 'node')) {
    Write-Fail 'Node.js is not installed or not on PATH.'
    Write-Host '    Install Node.js 18+ from https://nodejs.org/' -ForegroundColor Yellow
    Read-Host 'Press Enter to exit'
    exit 1
}
Write-Ok ("Node found:   " + (node --version))

# ---------- Backend setup ----------
Write-Step '[1/3] Setting up Flask backend'

Push-Location $BackendDir
try {
    $venvPython = Join-Path $BackendDir 'venv\Scripts\python.exe'

    if (-not (Test-Path $venvPython)) {
        Write-Host '    Creating Python virtual environment...'
        python -m venv venv
        if ($LASTEXITCODE -ne 0) { throw 'Failed to create virtual environment.' }
    }

    Write-Host '    Installing Python dependencies...'
    & $venvPython -m pip install -q --upgrade pip
    & $venvPython -m pip install -q -r requirements.txt
    if ($LASTEXITCODE -ne 0) { throw 'Failed to install Python dependencies.' }

    if ((-not (Test-Path '.env')) -and (Test-Path '.env.example')) {
        Copy-Item '.env.example' '.env'
    }

    Write-Host '    Ensuring admin user exists...'
    & $venvPython seed_admin.py 2>&1 | Out-Null

    Write-Ok 'Backend ready'
}
catch {
    Write-Fail $_.Exception.Message
    Pop-Location
    Read-Host 'Press Enter to exit'
    exit 1
}
Pop-Location

# ---------- Frontend setup ----------
Write-Step '[2/3] Setting up React frontend'

Push-Location $FrontendDir
try {
    if (-not (Test-Path 'node_modules')) {
        Write-Host '    Installing npm packages (first run only, may take a few minutes)...'
        npm install --silent --no-audit --no-fund
        if ($LASTEXITCODE -ne 0) { throw 'Failed to install npm packages.' }
    }
    Write-Ok 'Frontend ready'
}
catch {
    Write-Fail $_.Exception.Message
    Pop-Location
    Read-Host 'Press Enter to exit'
    exit 1
}
Pop-Location

# ---------- Start both services ----------
Write-Step '[3/3] Starting services'

# Backend: open new PowerShell window, activate venv, run Flask
$backendCmd = @"
`$Host.UI.RawUI.WindowTitle = 'Website Builder - BACKEND (port $BackendPort)'
Set-Location '$BackendDir'
& '$BackendDir\venv\Scripts\Activate.ps1'
`$env:FLASK_RUN_PORT = '$BackendPort'
python run.py
"@
Start-Process -FilePath 'powershell.exe' -ArgumentList '-NoExit', '-Command', $backendCmd
Write-Ok "Backend starting in new window (port $BackendPort)"

Start-Sleep -Seconds 3

# Frontend: open new PowerShell window, set env, run npm start
$frontendCmd = @"
`$Host.UI.RawUI.WindowTitle = 'Website Builder - FRONTEND (port $FrontendPort)'
Set-Location '$FrontendDir'
`$env:BROWSER = 'none'
`$env:REACT_APP_BACKEND_URL = 'http://localhost:$BackendPort'
npm start
"@
Start-Process -FilePath 'powershell.exe' -ArgumentList '-NoExit', '-Command', $frontendCmd
Write-Ok "Frontend starting in new window (port $FrontendPort)"

# ---------- Done ----------
Write-Host ''
Write-Host '==========================================================' -ForegroundColor Green
Write-Host '                       READY' -ForegroundColor Green
Write-Host '==========================================================' -ForegroundColor Green
Write-Host ''
Write-Host '  OPEN IN YOUR BROWSER:' -ForegroundColor White
Write-Host ''
Write-Host "      http://localhost:$FrontendPort" -ForegroundColor Cyan
Write-Host ''
Write-Host "  Backend API:  http://localhost:$BackendPort/api/health" -ForegroundColor Gray
Write-Host '  Admin login:  admin@websitebuilder.com / Admin@1234' -ForegroundColor Gray
Write-Host ''
Write-Host '  To stop: close both service windows' -ForegroundColor Gray
Write-Host ''
Write-Host '==========================================================' -ForegroundColor Green
Write-Host ''
Read-Host 'Press Enter to close this launcher'
