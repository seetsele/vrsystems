Run the orchestrator smoke test

Prerequisites:
- Python 3.10+ (3.14 used in development)
- Environment variables for providers you want to test (optional):
  - OPENAI_API_KEY
  - COHERE_API_KEY
  - ANTHROPIC_API_KEY
  - TOGETHER_API_KEY
  - OLLAMA_URL

Install dependencies:

```powershell
python -m pip install -r requirements-orchestrator.txt
```

Run smoke test (dummy mode if no keys provided):

```powershell
python python-tools/run_orchestrator_smoke.py
```

To run unit tests:

```powershell
python -m pip install pytest
python -m pytest -q tests/test_providers_normalization.py::test_provider_normalization
```
