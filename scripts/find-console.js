const fs = require('fs');
const path = require('path');
const log = require('./logger-node');

const root = path.resolve(__dirname, '..');
const include = ['public', 'desktop-app', 'browser-extension', 'scripts'];
const exts = ['.js', '.html'];
let found = [];

function walk(dir) {
  fs.readdirSync(dir).forEach(f => {
    const p = path.join(dir, f);
    // skip node_modules and other vendor folders
    if (p.split(path.sep).includes('node_modules') || p.split(path.sep).includes('.git')) return;
    const stat = fs.statSync(p);
    if (stat.isDirectory()) return walk(p);
    if (!exts.includes(path.extname(p))) return;
    const content = fs.readFileSync(p, 'utf8');
    const lines = content.split(/\r?\n/);
    lines.forEach((line, i) => {
      if (/\bconsole\.(log|debug)\s*\(/.test(line) && !/console\.debug\s*\(/.test(line)) {
        // ignore our own scripts that intentionally use console for output to user
        if (/scripts\\record-results\.js/.test(p) || /public\\assets\\js\\logger\.js/.test(p)) return;
        found.push(`${p}:${i+1}: ${line.trim()}`);
      }
    });
  });
}

include.forEach(dir => {
  const p = path.join(root, dir);
  if (fs.existsSync(p)) walk(p);
});

if (found.length) {
  log.error('Found console.log occurrences:\n' + found.join('\n'));
  process.exit(2);
} else {
  log.info('No console.log occurrences found in scanned paths.');
}
