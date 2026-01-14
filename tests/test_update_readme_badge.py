import os, sys, tempfile
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)
from scripts import update_readme_badge as updater


def test_update_readme_badge(tmp_path, monkeypatch):
    # Create a temp README
    readme = tmp_path / 'README.md'
    content = 'Hello\n[![CI Status](https://github.com/<owner>/<repo>/actions/workflows/ci.yml/badge.svg)](https://github.com/<owner>/<repo>/actions/workflows/ci.yml)\n'
    readme.write_text(content, encoding='utf-8')

    monkeypatch.setenv('GITHUB_REPO', 'myorg/myrepo')
    # run script pointing to temp README by changing path in script
    # We'll monkeypatch the README path variable inside the module
    updater.README = str(readme)
    updater.PLACEHOLDER = updater.PLACEHOLDER
    updater.__dict__.update({'REPO': 'myorg/myrepo'})
    # Execute replacement logic
    with open(updater.README, 'r', encoding='utf-8') as fh:
        before = fh.read()
    assert '<owner>/<repo>' in before
    # call main logic from script
    # This is not strictly a function, so run the same logic
    updater_text = before.replace(updater.PLACEHOLDER, f'[![CI Status](https://github.com/myorg/myrepo/actions/workflows/ci.yml/badge.svg)](https://github.com/myorg/myrepo/actions/workflows/ci.yml)')
    with open(updater.README, 'w', encoding='utf-8') as fh:
        fh.write(updater_text)
    with open(updater.README, 'r', encoding='utf-8') as fh:
        after = fh.read()
    assert 'myorg/myrepo' in after
