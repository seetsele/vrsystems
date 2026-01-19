// Minimal Node.js SDK stub for Verity API
const fetch = require('node-fetch');

class VerityClient {
  constructor(baseUrl, apiKey) {
    this.baseUrl = baseUrl.replace(/\/$/, '');
    this.apiKey = apiKey;
  }

  _headers() {
    const h = { Accept: 'application/json' };
    if (this.apiKey) h['Authorization'] = `Bearer ${this.apiKey}`;
    return h;
  }

  async moderate(content) {
    const res = await fetch(`${this.baseUrl}/api/moderate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...this._headers() },
      body: JSON.stringify({ content }),
    });
    return res.json();
  }
}

module.exports = { VerityClient };
