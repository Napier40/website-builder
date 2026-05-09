#!/usr/bin/env node
/**
 * Cross-platform stop script
 *
 * Kills any process listening on ports 5000 (backend) and 3000 (frontend).
 */
const { execSync } = require('child_process');

const PORTS = [5000, 3000];
const isWin = process.platform === 'win32';

function killPort(port) {
  try {
    if (isWin) {
      // Windows: find PID via netstat and kill it
      const out = execSync(`netstat -ano | findstr :${port}`, { encoding: 'utf8' });
      const pids = new Set();
      out.split('\n').forEach(line => {
        const match = line.trim().match(/\s+(\d+)$/);
        if (match) pids.add(match[1]);
      });
      pids.forEach(pid => {
        try {
          execSync(`taskkill /F /PID ${pid}`, { stdio: 'ignore' });
          console.log(`  ✓ Killed PID ${pid} on port ${port}`);
        } catch (e) { /* already dead */ }
      });
      if (pids.size === 0) console.log(`  · No process on port ${port}`);
    } else {
      // Unix: lsof or fuser
      try {
        const pid = execSync(`lsof -ti:${port}`, { encoding: 'utf8' }).trim();
        if (pid) {
          execSync(`kill -9 ${pid}`, { stdio: 'ignore' });
          console.log(`  ✓ Killed PID ${pid} on port ${port}`);
        } else {
          console.log(`  · No process on port ${port}`);
        }
      } catch (e) {
        console.log(`  · No process on port ${port}`);
      }
    }
  } catch (e) {
    console.log(`  · No process on port ${port}`);
  }
}

console.log('Stopping Website Builder services...');
PORTS.forEach(killPort);
console.log('Done.');
