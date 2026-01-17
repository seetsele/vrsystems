import http from 'k6/http';
import { sleep } from 'k6';

export let options = {
  stages: [
    { duration: '30s', target: 10 },
    { duration: '60s', target: 50 },
    { duration: '30s', target: 0 }
  ]
};

export default function () {
  // GET to TARGET_URL (fallback to local)
  http.get(__ENV.TARGET_URL || 'http://127.0.0.1:8001/');

  // POST verify payload
  let url = 'http://localhost:8000/verify';
  let payload = JSON.stringify({ claim: 'The sky is blue.' });
  let params = { headers: { 'Content-Type': 'application/json' } };
  http.post(url, payload, params);

  sleep(1);
}
