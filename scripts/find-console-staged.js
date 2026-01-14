#!/usr/bin/env node
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const log = require('./logger-node');

function getStagedFiles() {
  try {
    const out = execSync('git diff --cached --name-only --diff-filter=ACM', { encoding: 'utf8' });
    return out.split(/\r?\n/).filter(Boolean);
  } catch (e) {
    log.error('Failed to get staged files:', e.message);
    return [];
  }
}

const staged = getStagedFiles();
const exts = ['.js', '.html', '.ts', '.tsx'];
const includeDirs = ['public', 'desktop-app', 'browser-extension', 'scripts', 'verity-mobile'];

let found = [];

staged.forEach(f => {
  const p = path.resolve(f);
  if (!exts.includes(path.extname(p))) return;
  if (!fs.existsSync(p)) return;
  // ignore test files (they may intentionally contain console calls)
  if (p.includes(`${path.sep}tests${path.sep}`)) return;
  const content = fs.readFileSync(p, 'utf8');
  const lines = content.split(/\r?\n/);
  lines.forEach((line, i) => {
    if (/\bconsole\.(log|debug)\s*\(/.test(line) && !/console\.debug\s*\(/.test(line)) {
      // ignore intentional files
      if (/scripts\\record-results\.js/.test(p) || /public\\assets\\js\\logger\.js/.test(p)) return;
      found.push(`${p}:${i+1}: ${line.trim()}`);
    }
  });
});

if (found.length) {
  log.error('Found console.log occurrences in staged files:\n' + found.join('\n'));
  process.exit(2);
} else {
  log.info('No console.log occurrences found in staged files.');
  process.exit(0);
}
