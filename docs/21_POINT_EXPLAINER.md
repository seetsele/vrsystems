# The 21-Point Verification™ System — Explainer

Verity's 21-Point Verification™ System is our flagship methodology for automated, evidence-backed fact-checking. It is engineered to be rigorous, transparent, and human-understandable while remaining fast enough to serve live API traffic.

High-level summary
- 7 verification pillars × 3 checks each = 21 distinct verification points.
- Combines search-first research, multi-model AI consensus, source-authority scoring, and calibrated confidence (VeriScore™).
- Designed to surface supporting and contradicting evidence, quantify uncertainty, and generate an actionable human-readable summary.

Why 21 points?
- Each pillar targets a different dimension of truth: temporal relevance, source quality, direct evidence, model consensus, logic, reproducibility, and bias/intent.
- The 3-check structure ensures redundancy: different angles (e.g., author credibility, publisher authority, and primary/secondary status) minimize single-point failures.

Pillars & checks (concise):
1) Claim Parsing
  - Semantic extraction
  - Type classification (medical/finance/etc.)
  - Nuance/hedging detection
2) Temporal Verification
  - Claim currency detection
  - Source freshness scoring
  - Historical/timeframe mapping
3) Source Verification
  - Primary source identification
  - Source authority scoring
  - Source bias assessment
4) Evidence Aggregation
  - Multi-source corroboration
  - Counter-evidence detection
  - Expert consensus measurement
5) AI Multi-Model Consensus
  - Large model aggregation
  - Specialized model routing
  - Weighted ensemble voting
6) Logical & Contextual Analysis
  - Internal consistency
  - Statistical plausibility
  - Causal reasoning validation
7) Final Synthesis
  - Confidence calibration (VeriScore™)
  - Evidence quality scoring
  - Actionable summary generation with citations

What the system outputs
- `verdict`: `true|false|mixed|unverified`
- `veriscore`: calibrated 0-100 score summarizing pillar results
- `confidence_interval`: estimated range for the veriscore
- `verification_pillars`: per-pillar scores and per-check contributions
- `evidence_summary`: counts of supporting / contradicting sources, top citations
- `sources`: structured list of source objects (url, authority score, excerpt)

Marketing-friendly elevator pitch
"Verity's 21-Point Verification™ is an automated, multi-model fact-checking engine that applies 21 independent tests across seven pillars — pulling primary sources, weighting expert consensus, and returning a calibrated VeriScore™ with a human-readable explanation. It gives you the speed of AI with the rigor of domain experts."

Implementation notes for engineers
- Keep UI copy consistent: use `The 21-Point Verification System™` or `21-Point Verification™` where space is limited.
- Avoid renaming public assets in-place; update text nodes only to preserve layout and links.
- Provide per-pillar logs in debug mode for triage; store full evidence lists in `history` for reproducibility.

Examples
```json
{
  "verdict":"mixed",
  "veriscore":78.5,
  "confidence_interval":[72.0,85.0],
  "verification_pillars":{ "claim_parsing": {"score":95,"checks":3}, "temporal": {"score":80,"checks":3} }
}
```

If you want, I can also generate short marketing blurbs and microcopy for the desktop, mobile, extension, and API docs that use exactly the same font and style as current UI components.
