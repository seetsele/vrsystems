#!/usr/bin/env bash
echo "Running quick security audit (scaffold)."
echo "Python: pip-audit (if installed). Node: npm audit."

if command -v python3 >/dev/null 2>&1; then
  if python3 -m pip show pip_audit >/dev/null 2>&1; then
    echo "Running pip-audit..."
    python3 -m pip_audit
  else
    echo "pip-audit not installed. Install with: python3 -m pip install pip-audit"
  fi
fi

if [ -f package.json ]; then
  if command -v npm >/dev/null 2>&1; then
    echo "Running npm audit..."
    npm audit --audit-level=moderate || true
  fi
fi

echo "Security audit scaffold complete. Review findings and apply fixes." 
#!/usr/bin/env bash
set -euo pipefail

echo "Security audit helper - runs npm audit and pip-audit where available."

echo "Running npm audit (root and desktop-app)"
if command -v npm >/dev/null 2>&1; then
  npm audit --production || true
  if [ -d desktop-app ]; then
    (cd desktop-app && npm ci && npm audit --production) || true
  fi
else
  echo "npm not available in PATH"
fi

echo "Running pip-audit (if installed)"
if command -v pip-audit >/dev/null 2>&1; then
  pip-audit || true
else
  echo "pip-audit not installed; to install: python -m pip install pip-audit"
fi

echo "You should also run Snyk or other enterprise tools if available."
