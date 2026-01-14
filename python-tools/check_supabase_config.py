from dotenv import load_dotenv
import os, requests
load_dotenv('../.env')
svc = os.getenv('SUPABASE_SERVICE_KEY')
proj = 'zxgydzavblgetojqdtir'
url = f'https://api.supabase.com/v1/projects/{proj}/config/auth'
headers = {'Authorization': f'Bearer {svc}', 'Content-Type': 'application/json'}
print('Using service key present?', bool(svc))
r = requests.get(url, headers=headers, timeout=30)
print('status=', r.status_code)
print(r.text)
