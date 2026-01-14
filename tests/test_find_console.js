const { spawnSync } = require('child_process');
const fs = require('fs');
const os = require('os');
const path = require('path');
const assert = require('assert');

function writeTempFile(dir, name, contents) {
  const p = path.join(dir, name);
  fs.writeFileSync(p, contents, 'utf8');
  return p;
}

function runLinter(root) {
  const res = spawnSync(process.execPath, ['scripts/find-console.js'], { env: { ...process.env, FIND_CONSOLE_ROOT: root, FIND_CONSOLE_SCAN_ROOT: '1' }, encoding: 'utf8' });
  return res;
}

(async () => {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'find-console-'));
  try {
    // Case 1: file with console.log -> exit code 2 and truncated marker
    writeTempFile(tmp, 'bad.js', "console.log(\"" + 'a'.repeat(1000) + "\");\n");
    const r1 = runLinter(tmp);
    // exit code 2 indicates linter found hits
    assert.strictEqual(r1.status, 2, `expected status 2, got ${r1.status}; stdout:${r1.stdout} stderr:${r1.stderr}`);
    const out = r1.stdout + r1.stderr;
    assert.ok(out.includes('[truncated]') || out.includes('console.log'), 'expected truncated snippet or console.log in output');

    // Case 2: no console -> exit code 0
    fs.writeFileSync(path.join(tmp, 'good.js'), "const a = 1;\n");
    // remove bad file
    fs.unlinkSync(path.join(tmp, 'bad.js'));
    const r2 = runLinter(tmp);
    assert.strictEqual(r2.status, 0, `expected status 0, got ${r2.status}; stdout:${r2.stdout} stderr:${r2.stderr}`);

    console.log('ok');
  } finally {
    // cleanup
    fs.rmSync(tmp, { recursive: true, force: true });
  }
})();