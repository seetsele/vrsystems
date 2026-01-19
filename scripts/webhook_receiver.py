#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, HTTPServer
import json

class Receiver(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length) if length else b''
        try:
            payload = json.loads(body.decode('utf-8')) if body else {}
        except Exception:
            payload = {'raw': body.decode('utf-8', errors='ignore')}
        sig = self.headers.get('X-Webhook-Signature')
        print('RECEIVED', self.path, 'SIG=', sig)
        print(json.dumps(payload))
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'ok': True}).encode('utf-8'))

if __name__ == '__main__':
    server = HTTPServer(('127.0.0.1', 9000), Receiver)
    print('Webhook receiver listening on http://127.0.0.1:9000/webhook')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
