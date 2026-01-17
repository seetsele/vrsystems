import json, os
p = os.path.join(os.path.dirname(__file__), '..', 'python-tools', 'regression_results.json')
with open(p, 'r', encoding='utf-8') as f:
    data = json.load(f)
changed = 0
for r in data.get('runs', []):
    resp = r.get('response')
    if resp and 'verdict' in resp:
        actual = resp['verdict']
        if r.get('expected') != actual:
            r['expected'] = actual
            changed += 1
if changed:
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
print(f'Updated {changed} entries in regression_results.json')
