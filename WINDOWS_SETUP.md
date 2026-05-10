# Windows Setup Guide

This guide covers running the Website Builder on Windows, especially from **VS Code**.

---

## Prerequisites

- **Python 3.9+** — Install from https://www.python.org/downloads/ and check **"Add Python to PATH"** during install.
- **Node.js 18+** — Install from https://nodejs.org/ (LTS version recommended).
- **VS Code** — https://code.visualstudio.com/
- **Git** — https://git-scm.com/download/win

Verify:
```powershell
python --version
node --version
npm --version
```

---

## Option 1: One-command launch (easiest)

From the project root, double-click or run:

```batch
start.bat
```

Or use the PowerShell version (more robust, better error messages):

```powershell
powershell -ExecutionPolicy Bypass -File .\start.ps1
```

This will:
1. Create a Python virtual environment in `flask-backend\venv` (first time only)
2. Install all backend dependencies
3. Install all frontend dependencies
4. Launch **two separate console windows**:
   - **BACKEND** on port 5050
   - **FRONTEND** on port 3000

Then open http://localhost:3000 in your browser.

To stop: **close both console windows**.

---

## Option 2: VS Code Tasks

1. Open the project root in VS Code:  `code .`
2. Press **Ctrl+Shift+P** → type `Tasks: Run Task` → pick one:
   - **Development: Seed and Start** — First-time setup (seeds database then starts both servers)
   - **Full Stack: Start Both Servers** — Start backend + frontend in parallel
   - **Flask: Start Backend Server** — Backend only
   - **React: Start Dev Server** — Frontend only

> ⚠️ On Windows, the VS Code tasks call `python` directly. For those tasks to work, you must first **activate the virtual environment in VS Code's terminal** (see Option 3 below) OR run `start.bat` once to bootstrap the venv.

---

## Option 3: Manual (two terminals)

**Terminal 1 — Backend:**

```powershell
cd flask-backend
python -m venv venv                     # first time only
.\venv\Scripts\Activate.ps1             # every time
pip install -r requirements.txt         # first time only
python seed_templates.py                # first time only (optional seed data)
python seed_translations.py             # first time only (optional seed data)
python run.py
```

Keep this terminal open — backend runs on http://localhost:5050

**Terminal 2 — Frontend:**

```powershell
cd frontend
npm install                             # first time only
$env:REACT_APP_BACKEND_URL = "http://localhost:5050"
npm start
```

Keep this terminal open — frontend runs on http://localhost:3000

---

## Troubleshooting

### `"... was unexpected at this time."`

This is a Windows batch-file parsing error. If you see it in `start.bat`:
- **Pull the latest** — this was fixed in commit dated after 2026-05-10.
- The old script had unescaped parentheses inside an `echo` statement inside an `if` block, which `cmd.exe` misinterprets.
- If you still hit it, use **`start.ps1`** instead — it's immune to this class of bug.

### `'python' is not recognized as an internal or external command`

Python is not on PATH. Reinstall Python and tick **"Add Python to PATH"**, or add it manually:
```
C:\Users\<you>\AppData\Local\Programs\Python\Python3xx\
C:\Users\<you>\AppData\Local\Programs\Python\Python3xx\Scripts\
```

### `'node' is not recognized`

Same as above, install Node.js from https://nodejs.org/ (the installer adds it to PATH automatically).

### `ExecutionPolicy` error when running `start.ps1`

Windows blocks unsigned scripts by default. Two options:

**Temporary (recommended):**
```powershell
powershell -ExecutionPolicy Bypass -File .\start.ps1
```

**Permanent (for your user only):**
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

### Port 5050 or 3000 already in use

Find and kill the process:
```powershell
# For backend (5050)
netstat -ano | findstr :5050
taskkill /F /PID <PID>

# For frontend (3000)
netstat -ano | findstr :3000
taskkill /F /PID <PID>
```

### Backend starts but frontend says "Network Error" / CORS

The frontend expects the backend at `http://localhost:5050`. Make sure:
- The backend window shows `Running on http://127.0.0.1:5050`
- The frontend was started with `REACT_APP_BACKEND_URL=http://localhost:5050` (the start scripts do this automatically)

### `pip install` fails with SSL errors behind a corporate proxy

```powershell
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

### OneDrive-managed paths (e.g., `C:\Users\<you>\OneDrive\Documents\...`)

OneDrive usually works fine, but if you see strange file-locking errors:
- Pause OneDrive sync while running `npm install`
- Or clone the repo outside OneDrive (e.g., `C:\dev\website-builder`)

---

## VS Code tips for Windows

- **Default terminal:** In `Ctrl+Shift+P` → `Terminal: Select Default Profile`, pick **PowerShell** (not cmd).
- **Python interpreter:** `Ctrl+Shift+P` → `Python: Select Interpreter` → choose `.\flask-backend\venv\Scripts\python.exe`.
- **Debug Flask:** Press **F5** with `flask-backend\run.py` open — the included `.vscode\launch.json` is pre-configured for port 5050.

---

## File reference

| File | Purpose |
|---|---|
| `start.bat` | Windows batch launcher (cmd.exe) |
| `start.ps1` | Windows PowerShell launcher (recommended) |
| `start.sh` | macOS/Linux launcher |
| `.vscode\launch.json` | VS Code debug configurations |
| `.vscode\tasks.json` | VS Code task definitions |
| `.vscode\settings.json` | VS Code editor/Python/ESLint settings |
| `flask-backend\run.py` | Flask entry point |
| `flask-backend\requirements.txt` | Python dependencies |
| `frontend\package.json` | Node dependencies |
