import json
from pathlib import Path


def test_prompt_templates_file_exists_and_valid():
    p = Path(__file__).resolve().parents[2] / 'config' / 'prompt_templates.json'
    assert p.exists(), f"prompt templates file missing: {p}"
    data = json.loads(p.read_text(encoding='utf-8'))
    assert 'defaults' in data
    assert 'system_message' in data['defaults']
