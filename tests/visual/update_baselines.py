#!/usr/bin/env python3
"""
Copy screenshots from `playwright-report/screenshots/` into the visual baseline folder
when `UPDATE_BASELINES=1` is set. This script is intended to prepare a zip of updated
baselines for manual review; it does not commit changes.
"""
import os
import shutil
import time

SRC = os.path.join(os.getcwd(), 'playwright-report', 'screenshots')
DEST = os.path.join(os.getcwd(), 'tests', 'visual', 'baseline_updates')

if __name__ == '__main__':
    if os.environ.get('UPDATE_BASELINES', '').lower() not in ('1', 'true', 'yes'):
        print('UPDATE_BASELINES not set; exiting')
        raise SystemExit(0)

    if not os.path.exists(SRC):
        print('No screenshots found at', SRC)
        raise SystemExit(1)

    os.makedirs(DEST, exist_ok=True)
    ts = int(time.time())
    copied = 0
    for f in os.listdir(SRC):
        if f.lower().endswith('.png'):
            src = os.path.join(SRC, f)
            dest = os.path.join(DEST, f)
            shutil.copy2(src, dest)
            copied += 1
    print(f'Copied {copied} screenshots to {DEST} (ts={ts})')
    # create a zip for artifact upload
    import zipfile
    out = f'baseline-updates-{ts}.zip'
    with zipfile.ZipFile(out, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(DEST):
            for fn in files:
                full = os.path.join(root, fn)
                arc = os.path.relpath(full, start=DEST)
                z.write(full, arc)
    print('Wrote', out)
