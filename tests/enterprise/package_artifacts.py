import os
import time
import zipfile


def zip_paths(out_path, paths):
    with zipfile.ZipFile(out_path, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for p in paths:
            if not os.path.exists(p):
                continue
            if os.path.isdir(p):
                for root, dirs, files in os.walk(p):
                    for f in files:
                        full = os.path.join(root, f)
                        arc = os.path.relpath(full, start=os.path.dirname(p))
                        z.write(full, arc)
            else:
                z.write(p, os.path.basename(p))


if __name__ == '__main__':
    ts = int(time.time())
    out = f'artifacts-{ts}.zip'
    cwd = os.getcwd()
    candidates = [
        os.path.join(cwd, 'test-vault'),
        os.path.join(cwd, 'playwright-report'),
        os.path.join(cwd, 'playwright-results'),
    ]
    zip_paths(out, candidates)
    print(out)
