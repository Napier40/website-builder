#!/usr/bin/env node
/**
 * Cross-platform backend install helper
 *
 * - Creates flask-backend/venv if it doesn't exist
 * - Upgrades pip
 * - Installs requirements.txt
 *
 * Works on POSIX and Windows without shell-specific syntax.
 */
const { spawnSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const backendDir = path.join(__dirname, '..', 'flask-backend');
const venvDir    = path.join(backendDir, 'venv');
const reqFile    = path.join(__dirname, '..', 'requirements.txt');
const isWin      = process.platform === 'win32';

const venvPython = isWin
  ? path.join(venvDir, 'Scripts', 'python.exe')
  : path.join(venvDir, 'bin', 'python');

function run(cmd, args, opts = {}) {
  console.log(`\x1b[36m$ ${cmd} ${args.join(' ')}\x1b[0m`);
  const r = spawnSync(cmd, args, { stdio: 'inherit', ...opts });
  if (r.status !== 0) {
    process.exit(r.status ?? 1);
  }
}

// Pick a system python to bootstrap the venv
function pickSystemPython() {
  const candidates = isWin
    ? ['python', 'py']
    : ['python3', 'python'];
  for (const p of candidates) {
    const r = spawnSync(p, ['--version']);
    if (r.status === 0) return p;
  }
  console.error('\x1b[31mError: Could not find Python 3 on your PATH.\x1b[0m');
  console.error('       Install Python 3.9+ and try again.');
  process.exit(1);
}

// 1. Create venv if missing
if (!fs.existsSync(venvPython)) {
  const sysPy = pickSystemPython();
  console.log(`\x1b[36m[install:backend] Creating virtual environment...\x1b[0m`);
  run(sysPy, ['-m', 'venv', venvDir]);
} else {
  console.log(`\x1b[32m[install:backend] venv already exists ✓\x1b[0m`);
}

// 2. Upgrade pip
console.log(`\x1b[36m[install:backend] Upgrading pip...\x1b[0m`);
run(venvPython, ['-m', 'pip', 'install', '--quiet', '--upgrade', 'pip']);

// 3. Install requirements
console.log(`\x1b[36m[install:backend] Installing requirements.txt...\x1b[0m`);
run(venvPython, ['-m', 'pip', 'install', '--quiet', '-r', reqFile]);

console.log(`\x1b[32m[install:backend] Done ✓\x1b[0m`);
