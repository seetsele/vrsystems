(() => {
  const TESTS = [
    { method: 'GET', path: '/health' },
    { method: 'GET', path: '/health/deep' },
    { method: 'GET', path: '/providers' },
    { method: 'GET', path: '/providers/health' },
    { method: 'POST', path: '/verify', body: { claim: 'The sky is blue.', source: 'browser' } },
    { method: 'POST', path: '/v3/batch-verify', body: { claims: ['Water is wet.', 'The moon is made of cheese.'] } },
    { method: 'POST', path: '/tools/image-forensics', body: { image_url: 'https://example.com/sample.jpg' } },
    { method: 'POST', path: '/tools/realtime-stream', body: { text: 'This is a viral test message', metadata: { platform: 'browser' } } },
    { method: 'POST', path: '/tools/research-assistant', body: { query: 'recent research on misinformation detection' } },
    { method: 'POST', path: '/tools/social-media', body: { url: 'https://twitter.com/example/status/1' } },
    { method: 'POST', path: '/tools/source-credibility', body: { url: 'https://example.com/article' } },
    { method: 'POST', path: '/tools/statistics-validator', body: { text: '10% of people do X' } },
  ];

  const out = document.getElementById('out');
  const runBtn = document.getElementById('run');
  const dlBtn = document.getElementById('download');

  let results = [];

  async function run() {
    out.innerHTML = '';
    results = [];
    const base = document.getElementById('target').value.replace(/\/$/, '');
    const key = document.getElementById('key').value.trim();

    for (const t of TESTS) {
      const el = document.createElement('div');
      el.textContent = `${t.method} ${t.path} ...`;
      out.appendChild(el);
      try {
        const headers = { 'Content-Type': 'application/json' };
        if (key) headers['Authorization'] = `Bearer ${key}`;
        const res = await fetch(base + t.path, {
          method: t.method,
          headers,
          body: t.method === 'GET' ? null : JSON.stringify(t.body),
        });
        const text = await res.text();
        const ok = res.status === 200;
        el.innerHTML = `<strong>${t.method} ${t.path}</strong> - <span class="${ok ? 'ok' : 'fail'}">${res.status}</span>`;
        const pre = document.createElement('pre');
        pre.textContent = text;
        out.appendChild(pre);
        results.push({ test: t, status: res.status, body: text, ok });
      } catch (err) {
        el.innerHTML = `<strong>${t.method} ${t.path}</strong> - <span class="fail">error</span>`;
        const pre = document.createElement('pre');
        pre.textContent = String(err);
        out.appendChild(pre);
        results.push({ test: t, status: null, body: String(err), ok: false });
      }
      await new Promise(r => setTimeout(r, 200));
    }
  }

  runBtn.addEventListener('click', run);

  dlBtn.addEventListener('click', () => {
    const blob = new Blob([JSON.stringify({ time: Date.now(), results }, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `enterprise-results-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  });
})();
