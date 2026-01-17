Title: DLP-grade redaction and redaction policy tests

Description:
Strengthen the redaction system: add schema-aware redaction rules, tests that assert PII doesn't appear in run artifacts, and CI enforcement.

Checklist:
- [ ] Expand `redaction_patterns.json` with additional patterns and examples
- [ ] Add unit tests that run selected test suites and scan logs/JSON for PII patterns
- [ ] Add CI step that fails if PII patterns are detected in test outputs
- [ ] Consider integrating an external DLP tool or KMS-based filters for sensitive fields

Priority: Medium
