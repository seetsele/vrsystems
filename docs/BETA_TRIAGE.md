# Beta Test Failures Triage

Generated from `python-tools/comprehensive_test_results.json` (2026-01-15).

Summary
- Total tests in this run: 42
- Passed: 29
- Failed: 13
- Overall accuracy: 69.05%

Top failed tests (priority order)

1. `NH-003` (Nuanced Health) — Expected: `mixed`, Got: `false`
   - Claim preview: Red meat consumption is definitively linked to increased all-cause mortality...
   - Notes: short duration indicates possible provider error or parsing; increase provider diversity and add more evidence sources.

2. `NE-001` (Nuanced Economics) — Expected: `true`, Got: `mixed`
   - Claim preview: UBI programs as tested in Finland...
   - Notes: expert-level claim; ensure economic datasets and primary sources are weighted higher.

3. `ENV-001` (Nuanced Environment) — Expected: `true`, Got: `mixed`
   - Claim preview: Electric vehicles produce zero emissions during operation but their total lifecycle...
   - Notes: provider-specific nuance; adjust lifecycle analysis provider weights.

4. `TH-003` (True Historical) — Expected: `true`, Got: `false`
   - Claim preview: The 2024 Nobel Prize in Physics was awarded to John J. Hopfield and Geoffrey...
   - Notes: factual/history mismatch — add authoritative sources (Nobel.org) and caching for recent events.

5. `FM-003` (False Myths) — Expected: `false`, Got: `mixed`
   - Claim preview: The flat Earth theory is supported by measurable evidence...
   - Notes: misinformation class — tune confidence thresholds and source reliability.

6. `RE-002` (Recent Events 2024-2025) — Expected: `true`, Got: `false`
   - Claim preview: In November 2024, Donald Trump won the United States presidential election...
   - Notes: Recent events mismatch — validate news source freshness and caching TTLs.

7-12. Multiple `Adversarial` and `Technology Claims` tests failing — see full JSON for details.

Suggested immediate actions
- Increase provider diversity for failed categories and re-run tests.
- For True/Recent events, add authoritative sources (official press releases, Nobel, Reuters, AP).
- Lower weight of a provider that returned low-quality answers in these runs (investigate provider logs).
- Add targeted unit tests that reproduce the failing claim inputs (so fixes have regression tests).

Files
- Full results: `python-tools/comprehensive_test_results.json`
- Use this doc as the master triage list for beta bugfixes.
