from prometheus_client import start_http_server, Counter
from flask import Flask, jsonify

app = Flask(__name__)

VERIFY_COUNTER = Counter('verity_verify_requests_total', 'Total verify requests')


@app.route('/health')
def health():
    return jsonify({'status': 'ok'})


@app.route('/metrics')
def metrics():
    # prometheus_client provides its own /metrics endpoint; here we proxy to it
    return "", 204


def run_metrics_server(port: int = 8001):
    # Start prometheus client server on a different port
    start_http_server(port + 1)
    app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
    run_metrics_server()
