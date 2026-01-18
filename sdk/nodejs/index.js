const fetch = globalThis.fetch || require('node-fetch');

class VerityClient {
  constructor({ apiKey, baseUrl = 'http://127.0.0.1:8000' } = {}) {
    this.apiKey = apiKey;
    this.base = baseUrl.replace(/\/$/, '');
    this.headers = { Authorization: `Bearer ${this.apiKey}`, 'Content-Type': 'application/json' };
  }

  async verify(claim, tier = 'free') {
    const res = await fetch(`${this.base}/verify`, {
      method: 'POST',
      headers: this.headers,
      body: JSON.stringify({ claim, tier }),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  }

  // Minimal streaming compatibility: returns a Promise that resolves to the full result
  async *verifyStream(claim, tier = 'free') {
    const r = await this.verify(claim, tier);
    yield r;
  }
}

module.exports = { VerityClient };
