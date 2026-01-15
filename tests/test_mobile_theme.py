import re
from pathlib import Path


def extract_css_var(css_path, var_name):
    text = Path(css_path).read_text(encoding='utf-8')
    m = re.search(rf"{re.escape(var_name)}\s*:\s*([^;]+);", text)
    return m.group(1).strip() if m else None


def extract_ts_value(ts_path, key_name):
    text = Path(ts_path).read_text(encoding='utf-8')
    m = re.search(rf"{re.escape(key_name)}\s*:\s*'([^']+)'", text)
    return m.group(1).strip() if m else None


def test_mobile_accent_matches_public_theme():
    css_var = extract_css_var('public/assets/css/verity-theme.css', '--accent')
    assert css_var is not None, 'Could not find --accent in public theme CSS'

    amber = extract_ts_value('verity-mobile/src/theme/colors.ts', 'amber')
    assert amber is not None, 'Could not find amber value in mobile theme'

    # Normalize hex (lowercase)
    assert css_var.lower().startswith('#')
    assert amber.lower().startswith('#')

    assert css_var.lower() == amber.lower(), f"Mismatch: public --accent={css_var} vs mobile amber={amber}"
