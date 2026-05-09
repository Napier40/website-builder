#!/usr/bin/env node
/**
 * Post-install hook
 *
 * Runs after `npm install` at the repo root. Prints a friendly reminder
 * telling the user how to launch the app.
 */
const c = {
  reset: '\x1b[0m',
  bold:  '\x1b[1m',
  green: '\x1b[32m',
  cyan:  '\x1b[36m',
  yellow:'\x1b[33m',
  gray:  '\x1b[90m',
};

console.log('');
console.log(`${c.cyan}${c.bold}╔══════════════════════════════════════════════════════════╗${c.reset}`);
console.log(`${c.cyan}${c.bold}║   Website Builder — root dependencies installed ✓        ║${c.reset}`);
console.log(`${c.cyan}${c.bold}╚══════════════════════════════════════════════════════════╝${c.reset}`);
console.log('');
console.log(`  Next step — install the app's own dependencies (one-time):`);
console.log('');
console.log(`    ${c.green}${c.bold}npm run install:all${c.reset}`);
console.log('');
console.log(`  Then launch both services with a single command:`);
console.log('');
console.log(`    ${c.green}${c.bold}npm start${c.reset}`);
console.log('');
console.log(`  ${c.gray}Open http://localhost:3000 in your browser${c.reset}`);
console.log('');
