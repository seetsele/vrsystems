# Beta Onboarding Guide (short)

1. Install prerequisites

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r python-tools/requirements.txt
npm ci --prefix desktop-app
npm ci --prefix verity-mobile
```

2. Copy `.env.example` to `.env` and fill keys (see `docs/CI_SECRETS_INSTRUCTIONS.md`).

3. Start local services for testing

```powershell
cd python-tools
python api_server_v10.py
cd ..
cd public
python -m http.server 3001
```

4. Run smoke tests

```powershell
cd python-tools
python local_smoke_tests.py
```

5. Report bugs using `docs/BETA_TRIAGE.md` and open issues for failures.
