Title: docs: rename 9-point page to 21-point, add redirect, update tests

Summary
-------
Rename the legacy `9-point-system` documentation to the canonical `21-point-system` page, update tests to reference the new filename, and add a safe redirect at the old path to preserve external links.

Changes
-------
- Added `public/21-point-system.html` — exact visual copy with updated hero text: "The 21-Point Triple Verification System".
- Replaced `public/9-point-system.html` content with an immediate HTML redirect to `21-point-system.html` (keeps old URL working).
- Updated test `python-tools/tests/test_21_point_system.py` and generated test HTML in `public/tests/` to reference `21-point-system.html`.

Testing
-------
- Ran test suite under `python-tools`: `python -m pytest -q` — all tests passed (25 passed).

Notes
-----
- Keeping the redirect file ensures external links and bookmarks continue to work. If desired, we can remove the redirect in a follow-up after verifying there are no external dependencies.
- This change is surface-level (docs/tests) and does not affect runtime code.

Suggested reviewers: @frontend, @docs
