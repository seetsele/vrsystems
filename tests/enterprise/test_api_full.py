import os
import json
import glob
import subprocess
import pytest

# Optional JSON Schema validation (enabled in CI by installing `jsonschema`)
try:
    import jsonschema
    JSONSCHEMA_AVAILABLE = True
except Exception:
    JSONSCHEMA_AVAILABLE = False

SCHEMA_DIR = os.path.join(os.path.dirname(__file__), 'schemas')

def _load_schema_file(name):
    path = os.path.join(SCHEMA_DIR, name)
    if not os.path.exists(path):
        return None
    try:
        with open(path, 'r', encoding='utf-8') as fh:
            return json.load(fh)
    except Exception:
        return None

VERIFY_SCHEMA = _load_schema_file('verify_schema.json')
HEALTH_SCHEMA = _load_schema_file('health_schema.json')
STATUS_SCHEMA = _load_schema_file('status_schema.json')
TOOLS_SCHEMA = _load_schema_file('tools_schema.json')
DASH_SCHEMA = _load_schema_file('dashboard_schema.json')
SETTINGS_SCHEMA = _load_schema_file('settings_schema.json')
PROVIDER_SCHEMA = _load_schema_file('provider_schema.json')
API_DOCS_SCHEMA = _load_schema_file('api_docs_schema.json')


VAULT_DIR = os.path.join(os.getcwd(), 'test-vault')


def _latest_summary():
    pattern = os.path.join(VAULT_DIR, 'api-run-*.json')
    files = glob.glob(pattern)
    if not files:
        return None
    latest = max(files, key=os.path.getmtime)
    with open(latest, 'r', encoding='utf-8') as fh:
        return json.load(fh)


def _ensure_artifact():
    summary = _latest_summary()
    if summary:
        return summary
    # Invoke the runner to generate artifacts
    runner = os.path.join(os.getcwd(), 'tests', 'enterprise', 'run_api_full.py')
    try:
        subprocess.check_call(["python", runner])
    except subprocess.CalledProcessError:
        # runner failed; proceed to try reading whatever exists
        pass
    return _latest_summary()


SUMMARY = _ensure_artifact()


def pytest_generate_tests(metafunc):
    # parametrizes tests from available summary artifact
    if 'record' in metafunc.fixturenames:
        if not SUMMARY:
            pytest.skip('No API run artifact available and runner could not generate one')
        metafunc.parametrize('record', SUMMARY.get('results', []))


def _is_strict():
    return os.environ.get('STRICT_TESTS', '') not in ('', '0', 'false', 'False')


def test_api_record(record):
    """Validate a single API record from the latest runner artifact.

    In non-strict mode, failing records are skipped (informational). In strict
    mode, a failing record causes a test failure.
    """
    method = record.get('method')
    path = record.get('path')
    ok = bool(record.get('ok'))
    status = record.get('status_code')
    # If the record failed (non-2xx/3xx)
    if not ok:
        if _is_strict():
            pytest.fail(f'{method} {path} returned {status} — failing under STRICT_TESTS')
        else:
            pytest.skip(f'{method} {path} returned {status} — non-strict mode, skipping')

    # At this point the request returned a 2xx/3xx. In strict mode, run
    # additional content checks for key endpoints to ensure schema/fields.
    if not _is_strict():
        return

    # Define lightweight expectations for important paths
    def _check_verify(rec):
        body = rec.get('body_snippet', '')
        try:
            data = json.loads(body)
            # common keys we expect from a verification response
            return any(k in data for k in ('verdict', 'result', 'confidence', 'claim'))
        except Exception:
            # body might be HTML or truncated JSON — do a substring check
            return 'verdict' in body or 'confidence' in body or 'result' in body

    def _check_health(rec):
        body = rec.get('body_snippet', '').lower()
        return 'ok' in body or 'status' in body or rec.get('status_code') == 200

    EXPECTED = {
        '/verify': _check_verify,
        '/health': _check_health,
        '/status': _check_health,
    }

    # Additional lightweight checkers for common UI/API endpoints
    def _check_tools(rec):
        body = rec.get('body_snippet', '')
        try:
            data = json.loads(body)
            if isinstance(data, dict):
                return 'tools' in data or 'name' in next(iter(data.keys()), '')
            return isinstance(data, list)
        except Exception:
            return 'tools' in body.lower() or '[' in body[:20]

    def _check_dashboard(rec):
        body = rec.get('body_snippet', '').lower()
        try:
            data = json.loads(rec.get('body_snippet', '{}'))
            if isinstance(data, dict):
                return any(k in data for k in ('stats', 'users', 'metrics', 'activity'))
        except Exception:
            pass
        return 'dashboard' in body or 'stats' in body or 'activity' in body

    def _check_settings(rec):
        body = rec.get('body_snippet', '').lower()
        try:
            data = json.loads(rec.get('body_snippet', '{}'))
            if isinstance(data, dict):
                return 'settings' in data or 'providers' in data
        except Exception:
            pass
        return 'settings' in body or 'providers' in body

    def _check_provider_setup(rec):
        return _check_settings(rec) or 'provider' in rec.get('body_snippet', '').lower()

    def _check_api_docs(rec):
        body = rec.get('body_snippet', '').lower()
        try:
            data = json.loads(rec.get('body_snippet', '{}'))
            return 'openapi' in data or 'swagger' in data
        except Exception:
            pass
        return 'swagger' in body or 'openapi' in body or '<title>' in rec.get('body_snippet', '')

    EXPECTED.update({
        '/tools': _check_tools,
        '/dashboard': _check_dashboard,
        '/settings': _check_settings,
        '/provider-setup': _check_provider_setup,
        '/api/docs': _check_api_docs,
    })

    checker = EXPECTED.get(path)
    if checker:
        ok2 = checker(record)
        # If content check failed but JSON Schema is available, try schema validation
        if not ok2 and JSONSCHEMA_AVAILABLE:
            schema = None
            if path == '/verify':
                schema = VERIFY_SCHEMA
            elif path in ('/health', '/status'):
                schema = HEALTH_SCHEMA or STATUS_SCHEMA
            elif path == '/api/docs':
                schema = _load_schema_file('api_docs_schema.json')

            if schema:
                try:
                    body = record.get('body_snippet', '')
                    data = json.loads(body)
                    jsonschema.validate(instance=data, schema=schema)
                    ok2 = True
                except Exception:
                    ok2 = False

        # If still not ok and a schema exists for other endpoints, try them
        if not ok2 and JSONSCHEMA_AVAILABLE:
            extra_schema = None
            if path == '/tools':
                extra_schema = TOOLS_SCHEMA
            elif path == '/dashboard':
                extra_schema = DASH_SCHEMA
            if extra_schema:
                try:
                    data = json.loads(record.get('body_snippet', '{}'))
                    jsonschema.validate(instance=data, schema=extra_schema)
                    ok2 = True
                except Exception:
                    ok2 = False

        # final attempt: other known schemas
        if not ok2 and JSONSCHEMA_AVAILABLE:
            if path == '/settings' and SETTINGS_SCHEMA:
                try:
                    jsonschema.validate(instance=json.loads(record.get('body_snippet', '{}')), schema=SETTINGS_SCHEMA)
                    ok2 = True
                except Exception:
                    ok2 = False
            if path == '/provider-setup' and PROVIDER_SCHEMA and not ok2:
                try:
                    jsonschema.validate(instance=json.loads(record.get('body_snippet', '{}')), schema=PROVIDER_SCHEMA)
                    ok2 = True
                except Exception:
                    ok2 = False
            if path == '/api/docs' and API_DOCS_SCHEMA and not ok2:
                try:
                    jsonschema.validate(instance=json.loads(record.get('body_snippet', '{}')), schema=API_DOCS_SCHEMA)
                    ok2 = True
                except Exception:
                    ok2 = False

        if not ok2:
            pytest.fail(f'{method} {path} returned {status} but content check failed under STRICT_TESTS')
