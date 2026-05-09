#!/usr/bin/env node
/**
 * Cross-platform backend launcher
 *
 * Finds the Python executable inside flask-backend/venv (works on both
 * POSIX and Windows because each has a different venv layout) and runs
 * run.py directly — no `source activate` needed.
 */
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const backendDir = path.join(__dirname, '..', 'flask-backend');
const isWin = process.platform === 'win32';

// Figure out which python to use.
// Prefer venv python (created by `npm run install:backend`); fall back to system.
const venvPython = isWin
  ? path.join(backendDir, 'venv', 'Scripts', 'python.exe')
  : path.join(backendDir, 'venv', 'bin', 'python');

let pythonCmd;
if (fs.existsSync(venvPython)) {
  pythonCmd = venvPython;
} else {
  console.warn('\x1b[33m[start:backend] No venv found — using system python.\x1b[0m');
  console.warn('\x1b[33m                Run `npm run install:backend` first for a proper setup.\x1b[0m');
  pythonCmd = isWin ? 'python' : 'python3';
}

const runPy = path.join(backendDir, 'run.py');

const child = spawn(pythonCmd, [runPy], {
  cwd: backendDir,
  stdio: 'inherit',
  env: { ...process.env, PYTHONUNBUFFERED: '1' },
});

child.on('exit', (code, signal) => {
  if (signal) {
    process.exit(0);
  }
  process.exit(code ?? 0);
});

// Forward Ctrl+C etc.
['SIGINT', 'SIGTERM'].forEach(sig => {
  process.on(sig, () => {
    if (!child.killed) child.kill(sig);
  });
});
