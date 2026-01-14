const fs = require('fs');
const path = require('path');
const log = require('../../scripts/logger-node');

function timestamp() {
  const d = new Date();
  return d.toISOString().replace(/[:.]/g, '-');
}

function ensureDir(p) {
  if (!fs.existsSync(p)) fs.mkdirSync(p, { recursive: true });
}

async function main() {
  const args = process.argv.slice(2);
  if (args.length < 2) {
    log.error('Usage: node record-results.js <suite> <srcResultFile>');
    process.exit(1);
  }
  const [suite, src] = args;
  if (!fs.existsSync(src)) {
    log.error('Source results file not found:', src);
    process.exit(1);
  }

  ensureDir(path.resolve(__dirname, '..', 'test-results'));
  ensureDir(path.resolve(__dirname, '..', '..', 'test-vault'));

  const payload = fs.readFileSync(src, 'utf8');
  const meta = {
    suite,
    recordedAt: new Date().toISOString(),
    nodeVersion: process.version,
    cwd: process.cwd(),
  };

  const out = {
    meta,
    results: JSON.parse(payload)
  };

  const outPath = path.resolve(__dirname, '..', '..', 'test-vault', `${suite}-${timestamp()}.json`);
  fs.writeFileSync(outPath, JSON.stringify(out, null, 2));
  log.info('Recorded test results to', outPath);
}

main().catch(e => { log.error(e); process.exit(1); });