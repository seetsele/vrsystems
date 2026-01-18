import requests
import sys

def main():
    try:
        r = requests.post('http://127.0.0.1:8000/verify', json={'claim': 'smoke-test'})
        print('STATUS', r.status_code)
        print(r.text)
    except Exception as e:
        print('ERROR', e, file=sys.stderr)

if __name__ == '__main__':
    main()
