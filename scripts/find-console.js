const fs = require('fs');
const path = require('path');
const log = require('./logger-node');

const root = process.env.FIND_CONSOLE_ROOT || path.resolve(__dirname, '..');
const MAX_SNIPPET = 240; // max length for matched line snippets to keep output concise
const TRUNCATION_MARK = '... [truncated]';
const include = ['public', 'desktop-app', 'browser-extension', 'scripts', 'verity-mobile'];
const exts = ['.js', '.html', '.ts', '.tsx'];
let found = [];

function walk(dir) {
  fs.readdirSync(dir).forEach(f => {
    const p = path.join(dir, f);
    // skip node_modules, build outputs and other vendor folders
    if (p.split(path.sep).includes('node_modules') || p.split(path.sep).includes('.git')) return;
    // skip common build/output folders (e.g., android/build, **/build/**, dist, out)
    if (p.includes(`${path.sep}build${path.sep}`) || p.includes(`${path.sep}dist${path.sep}`) || p.includes(`${path.sep}out${path.sep}`)) return;
    const stat = fs.statSync(p);
    if (stat.isDirectory()) return walk(p);
    if (!exts.includes(path.extname(p))) return;
    let content;
    try {
      content = fs.readFileSync(p, 'utf8');
    } catch (err) {
      log.error('Error reading file ' + p + ': ' + err.message);
      process.exit(1);
    }
    const lines = content.split(/\r?\n/);
    lines.forEach((line, i) => {
      if (/\bconsole\.(log|debug)\s*\(/.test(line) && !/console\.debug\s*\(/.test(line)) {
        // ignore our own scripts that intentionally use console for output to user
        if (/scripts\\record-results\.js/.test(p) || /public\\assets\\js\\logger\.js/.test(p)) return;
        // truncate long lines to avoid huge, unreadable CI logs
        let snippet = line.trim();
        if (snippet.length > MAX_SNIPPET) snippet = snippet.slice(0, MAX_SNIPPET - TRUNCATION_MARK.length) + TRUNCATION_MARK;
        found.push(`${p}:${i+1}: ${snippet}`);
      }
    });
  });
}

// If FIND_CONSOLE_SCAN_ROOT=1 is set, scan the provided root directory directly (useful for tests)
if (process.env.FIND_CONSOLE_ROOT && process.env.FIND_CONSOLE_SCAN_ROOT === '1') {
  if (fs.existsSync(root)) walk(root);
} else {
  include.forEach(dir => {
    const p = path.join(root, dir);
    if (fs.existsSync(p)) walk(p);
  });
}

if (found.length) {
  log.error('Found console.log occurrences:\n' + found.join('\n'));
  process.exit(2);
} else {
  log.info('No console.log occurrences found in scanned paths.');
}
