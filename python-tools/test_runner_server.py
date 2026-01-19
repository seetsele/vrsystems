#!/usr/bin/env python3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import tempfile
from pathlib import Path
import xml.etree.ElementTree as ET
import json
import os

# integration adapters (optional)
try:
    from python_tools import integrations
except Exception:
    integrations = None
ROOT = Path(__file__).resolve().parents[1]

# import helpers from the simple_test_api fallback so features are consistent
import sys
sys.path.insert(0, str(ROOT / 'python-tools'))
try:
    import simple_test_api as st
except Exception:
    st = None

app = FastAPI(title="Local Test Runner")
# security / CORS configuration (override with env vars)
TEST_RUNNER_API_KEY = os.getenv('TEST_RUNNER_API_KEY', '')
ALLOW_ORIGINS = os.getenv('TEST_RUNNER_ALLOW_ORIGINS', 'http://127.0.0.1:3001').split(',')
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOW_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


from fastapi import Request, Depends


def verify_api_key(request: Request):
    key = TEST_RUNNER_API_KEY
    if not key:
        return True
    header = request.headers.get('x-test-runner-key') or request.headers.get('authorization')
    if header:
        if header.lower().startswith('bearer '):
            token = header.split(' ', 1)[1]
        else:
            token = header
        if token == key:
            return True
    raise HTTPException(status_code=401, detail='Unauthorized to use test-runner')


from typing import Optional, List, Dict


class RunRequest(BaseModel):
    target: Optional[str] = "tests"  # 'tests', 'python-tools/tests', or 'all'
    # run specific pytest node ids or file paths, e.g. ['tests/test_foo.py::test_bar']
    items: Optional[List[str]] = None
    # convenience single item
    item: Optional[str] = None
    # pytest marker expression, e.g. 'integration and not slow'
    marker: Optional[str] = None
    # optional environment variables to inject during the run
    env: Optional[Dict[str, str]] = None
    # timeout in seconds for the pytest subprocess
    timeout: Optional[int] = 1800


def parse_junit(xml_path: Path):
    if not xml_path.exists():
        return {}
    tree = ET.parse(xml_path)
    root = tree.getroot()
    summary = {
        'total': 0,
        'passed': 0,
        'failed': 0,
        'skipped': 0,
        'time': float(root.attrib.get('time', 0.0)) if 'time' in root.attrib else 0.0,
    }
    tests = []
    for tc in root.iter('testcase'):
        summary['total'] += 1
        name = tc.attrib.get('name')
        classname = tc.attrib.get('classname')
        time = float(tc.attrib.get('time', 0.0))
        outcome = 'passed'
        message = ''
        for child in tc:
            if child.tag in ('failure', 'error'):
                outcome = 'failed'
                message = child.text or ''
            elif child.tag == 'skipped':
                outcome = 'skipped'
                message = child.attrib.get('message', '') or (child.text or '')
        if outcome == 'passed':
            summary['passed'] += 1
        elif outcome == 'failed':
            summary['failed'] += 1
        elif outcome == 'skipped':
            summary['skipped'] += 1

        tests.append({
            'name': name,
            'classname': classname,
            'time': time,
            'outcome': outcome,
            'message': message,
        })

    return {'summary': summary, 'tests': tests}


@app.on_event('startup')
def startup_event():
    # Initialize Sentry if DSN present (best-effort)
    try:
        SENTRY_DSN = os.getenv('SENTRY_DSN')
        if SENTRY_DSN:
            import sentry_sdk
            sentry_sdk.init(dsn=SENTRY_DSN, traces_sample_rate=float(os.getenv('SENTRY_TRACES_SAMPLE_RATE', '0.1')))
            print('Sentry initialized for FastAPI runner')
    except Exception:
        pass


@app.get('/health')
def health():
    return {'status': 'ok'}


@app.get('/metrics')
def metrics():
    # lightweight metrics for local dev; if simple_test_api available, include run counts
    m = {'app': 'test-runner', 'status': 'running'}
    try:
        if st:
            a = st.get_analytics()
            m['total_runs'] = a.get('total_runs', 0)
            m['total_failed'] = a.get('total_failed', 0)
    except Exception:
        pass
    return m


@app.get('/prometheus')
def prometheus_metrics():
    # return Prometheus exposition format
    try:
        lines = []
        if st:
            try:
                # call into fallback to compute same metrics
                import sqlite3
                conn = sqlite3.connect(str(st.DB_PATH))
                cur = conn.cursor()
                cur.execute('SELECT COUNT(1) FROM runs')
                total_runs = cur.fetchone()[0]
                cur.execute('SELECT COUNT(1) FROM runs WHERE exit_code!=0')
                failed_runs = cur.fetchone()[0]
                cur.execute("SELECT COUNT(1) FROM webhook_queue WHERE status IN ('queued','retry')")
                queued = cur.fetchone()[0]
                cur.execute('SELECT COUNT(1) FROM webhook_deliveries WHERE status=\'failed\'')
                failed_deliveries = cur.fetchone()[0]
                cur.execute('SELECT COUNT(1) FROM providers')
                providers = cur.fetchone()[0]
                conn.close()
                lines.append('# TYPE verity_total_runs counter')
                lines.append(f'verity_total_runs {int(total_runs)}')
                lines.append('# TYPE verity_failed_runs counter')
                lines.append(f'verity_failed_runs {int(failed_runs)}')
                lines.append('# TYPE verity_webhook_queue gauge')
                lines.append(f'verity_webhook_queue {int(queued)}')
                lines.append('# TYPE verity_webhook_failed_deliveries counter')
                lines.append(f'verity_webhook_failed_deliveries {int(failed_deliveries)}')
                lines.append('# TYPE verity_providers_total gauge')
                lines.append(f'verity_providers_total {int(providers)}')
            except Exception:
                pass
        body = '\n'.join(lines) + '\n'
        from fastapi.responses import PlainTextResponse
        return PlainTextResponse(body, media_type='text/plain; version=0.0.4')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/analytics')
def analytics():
    if st:
        try:
            return st.get_analytics()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    raise HTTPException(status_code=404, detail='analytics backend not available')


class TextPayload(BaseModel):
    text: str


class TextsPayload(BaseModel):
    texts: List[str]


@app.post('/api/moderate', dependencies=[Depends(verify_api_key)])
def api_moderate(body: TextPayload):
    if not integrations:
        raise HTTPException(status_code=503, detail='integrations not available')
    try:
        res = integrations.moderation.moderate(body.text)
        return {'result': res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/api/embed', dependencies=[Depends(verify_api_key)])
def api_embed(body: TextsPayload):
    if not integrations:
        raise HTTPException(status_code=503, detail='integrations not available')
    try:
        vecs = integrations.embeddings.embed(body.texts)
        return {'vectors': vecs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class LLMRequest(BaseModel):
    prompt: str
    max_tokens: Optional[int] = 256


@app.post('/api/llm', dependencies=[Depends(verify_api_key)])
def api_llm(req: LLMRequest):
    if not integrations:
        raise HTTPException(status_code=503, detail='integrations not available')
    try:
        out = integrations.llm.generate(req.prompt, max_new_tokens=req.max_tokens)
        return {'text': out}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/api/maps/geocode')
def api_geocode(body: TextPayload):
    if not integrations:
        raise HTTPException(status_code=503, detail='integrations not available')
    try:
        out = integrations.maps.geocode_nominatim(body.text)
        return {'result': out}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class StreamRequest(BaseModel):
    provider: str
    target: Optional[str] = None


@app.post('/api/stream/fetch', dependencies=[Depends(verify_api_key)])
def api_stream_fetch(req: StreamRequest):
    if not integrations:
        raise HTTPException(status_code=503, detail='integrations not available')
    try:
        if req.provider == 'reddit':
            # fetch small sample via reddit RSS fallback
            import requests
            sub = req.target or 'all'
            feed = f'https://www.reddit.com/r/{sub}/new/.rss'
            r = requests.get(feed, headers={'User-Agent': 'verity-stream'}, timeout=10)
            return {'rss': r.text[:2000]}
        elif req.provider == 'mastodon':
            # attempt to call Mastodon timeline if mastodon.py installed
            try:
                from mastodon import Mastodon
                instance = req.target or os.environ.get('MASTODON_INSTANCE')
                if not instance:
                    raise RuntimeError('no mastodon instance configured')
                m = Mastodon(api_base_url=instance, access_token=os.environ.get('MASTODON_TOKEN'))
                timeline = m.timeline_home(limit=10)
                return {'items': timeline}
            except Exception as e:
                raise
        else:
            raise HTTPException(status_code=400, detail='unknown provider')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/audit', dependencies=[Depends(verify_api_key)])
def audit_list():
    if st:
        try:
            return {'audit': st.list_audit()}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    raise HTTPException(status_code=404, detail='audit backend not available')


@app.get('/providers')
def providers_list():
    if st:
        try:
            return {'providers': st.list_providers()}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    raise HTTPException(status_code=404, detail='providers backend not available')


@app.post('/providers', dependencies=[Depends(verify_api_key)])
def providers_create(body: dict):
    if st:
        name = body.get('name')
        secret = body.get('secret')
        if not name:
            raise HTTPException(status_code=400, detail='missing name')
        try:
            pid = st.create_provider(name, secret or '')
            return {'id': pid}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    raise HTTPException(status_code=404, detail='providers backend not available')


@app.get('/redaction-patterns')
def redaction_get():
    if st:
        try:
            return {'patterns': st.load_redaction_patterns()}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    raise HTTPException(status_code=404, detail='redaction backend not available')


@app.post('/redaction-patterns', dependencies=[Depends(verify_api_key)])
def redaction_update(body: dict):
    pats = body.get('patterns')
    if not isinstance(pats, list):
        raise HTTPException(status_code=400, detail='missing patterns list')
    try:
        pfile = ROOT / 'python-tools' / 'redaction_patterns.json'
        pfile.parent.mkdir(parents=True, exist_ok=True)
        pfile.write_text(json.dumps({'patterns': pats}, indent=2), encoding='utf-8')
        return {'status': 'ok'}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/run-tests', dependencies=[Depends(verify_api_key)])
def run_tests(req: RunRequest):
    # assemble pytest arguments depending on request
    target = (req.target or 'tests')
    extra_flags = []
    if req.items:
        args = list(req.items)
    elif req.item:
        args = [req.item]
    elif req.marker:
        extra_flags = ['-m', req.marker]
        if target == 'all':
            args = ['.']
        else:
            args = [target]
    else:
        if target == 'all':
            args = ['.']
        elif target == 'python-tools':
            args = ['python-tools/tests']
        else:
            args = [target]

    timeout = req.timeout or 1800

    with tempfile.TemporaryDirectory() as td:
        tdpath = Path(td)
        junit = tdpath / 'results.xml'
        # Run pytest and capture output
        cmd = ['python', '-m', 'pytest', '-q', '--junitxml', str(junit)] + extra_flags + args
        try:
            env = os.environ.copy()
            if req.env:
                for k, v in (req.env or {}).items():
                    env[str(k)] = str(v)

            proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=timeout, env=env)
        except subprocess.TimeoutExpired:
            raise HTTPException(status_code=504, detail='Test run timed out')

        stdout = proc.stdout
        stderr = proc.stderr
        rc = proc.returncode

        parsed = parse_junit(junit)

        return {
            'exit_code': rc,
            'stdout': stdout,
            'stderr': stderr,
            'parsed': parsed,
            'cmd': cmd,
        }


if __name__ == '__main__':
    import uvicorn
    # run app object directly to avoid module path issues when folder name contains hyphens
    uvicorn.run(app, host='127.0.0.1', port=8010, log_level='info')
