#!/usr/bin/env python3
"""Format a consensus JSON output into a professional TXT and (optional) PDF report.

Usage:
  python scripts/format_consensus_report.py [input_file]

If `reportlab` is installed the script will also generate a PDF. Otherwise it will
produce a TXT report only.
"""
import json
import os
import re
import sys
from datetime import datetime


def load_json_from_file(path):
    text = open(path, "r", encoding="utf-8").read()
    # Try direct JSON
    try:
        return json.loads(text)
    except Exception:
        pass
    # Try to find first JSON object in the file
    m = re.search(r"\{[\s\S]*\}", text)
    if m:
        try:
            return json.loads(m.group(0))
        except Exception:
            pass
    raise ValueError("No JSON object found in file: %s" % path)


def safe_get(d, *keys, default=None):
    v = d
    for k in keys:
        if not isinstance(v, dict):
            return default
        v = v.get(k, default)
    return v


def format_pillar_breakdown(b):
    if not isinstance(b, dict):
        return str(b)
    lines = []
    for k, v in sorted(b.items()):
        lines.append(f"- {k}: {v}")
    return "\n".join(lines)


def build_text_report(consensus):
    parts = []
    meta = consensus.get("meta", {})
    header = [
        "Comprehensive Verification Report",
        f"Generated: {datetime.utcnow().isoformat()}Z",
    ]
    parts.append("\n".join(header))
    parts.append("=" * 72)

    verdict = safe_get(consensus, "verdict") or safe_get(consensus, "final_verdict")
    confidence = safe_get(consensus, "confidence")
    veriscore = safe_get(consensus, "veriscore") or safe_get(consensus, "score")
    processing = safe_get(consensus, "processing_time_seconds")

    parts.append(f"Final verdict: {verdict}")
    parts.append(f"Confidence: {confidence}")
    parts.append(f"VeriScore: {veriscore}")
    parts.append(f"Processing time (s): {processing}")

    parts.append("\nProviders used:")
    provs = consensus.get("providers_used") or consensus.get("providers") or []
    if isinstance(provs, list):
        parts.append(", ".join(provs))
    else:
        parts.append(str(provs))

    parts.append("\nPillar breakdown:")
    parts.append(format_pillar_breakdown(consensus.get("pillar_breakdown") or consensus.get("pillars") or {}))

    parts.append("\nPer-round provider stamps:")
    rounds = consensus.get("rounds") or consensus.get("providers_per_round") or []
    if isinstance(rounds, list) and rounds:
        for i, r in enumerate(rounds, start=1):
            parts.append(f"Round {i}: {r}")
    else:
        # sometimes providers are listed with suffixes (provider_r1..)
        pu = provs
        parts.append(str(pu))

    parts.append("\nExtracted notable sources and snippets:")
    sources = consensus.get("sources") or meta.get("sources") or []
    if isinstance(sources, list) and sources:
        for s in sources:
            if isinstance(s, dict):
                title = s.get("title") or s.get("url") or s.get("id")
                snippet = s.get("snippet") or s.get("excerpt") or ""
                parts.append(f"- {title}: {snippet}")
            else:
                parts.append(f"- {s}")
    else:
        parts.append("(no sources present in consensus JSON)")

    parts.append("\nProvider reasoning (sample):")
    prov_reasons = consensus.get("provider_reasons") or consensus.get("provider_responses") or {}
    if isinstance(prov_reasons, dict) and prov_reasons:
        for p, r in prov_reasons.items():
            snippet = r if isinstance(r, str) else json.dumps(r, ensure_ascii=False)[:1000]
            parts.append(f"- {p}: {snippet}")
    else:
        parts.append("(no provider reasoning captured)")

    parts.append("\nFull consensus JSON is attached as a machine-readable artifact.")

    return "\n\n".join(parts)


def write_txt_report(out_path, text):
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text)


def write_pdf_report(out_path, text):
    try:
        from reportlab.lib.pagesizes import LETTER
        from reportlab.lib.units import inch
        from reportlab.pdfgen import canvas
    except Exception as e:
        raise

    c = canvas.Canvas(out_path, pagesize=LETTER)
    width, height = LETTER
    left = 0.75 * inch
    top = height - 0.75 * inch
    max_width = width - 1.5 * inch
    lines = text.splitlines()
    y = top
    line_height = 12
    for line in lines:
        # wrap long lines
        while len(line) > 0:
            # Estimate characters that fit
            if len(line) <= 90:
                chunk = line
                line = ""
            else:
                chunk = line[:90]
                # try to cut at last space
                sp = chunk.rfind(" ")
                if sp > 40:
                    chunk = chunk[:sp]
                    line = line[sp + 1 :]
                else:
                    line = line[90:]
            c.drawString(left, y, chunk)
            y -= line_height
            if y < 0.75 * inch:
                c.showPage()
                y = top
    c.save()


def main():
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        path = "COMPREHENSIVE_VERIFICATION_OUTPUT.txt"

    if not os.path.exists(path):
        print("Input file not found:", path)
        sys.exit(2)

    try:
        consensus = load_json_from_file(path)
    except Exception as e:
        print("Failed to parse JSON from input:", e)
        sys.exit(3)

    text = build_text_report(consensus)
    txt_out = path + ".report.txt"
    write_txt_report(txt_out, text)
    print("TXT report written:", txt_out)

    # Attempt PDF generation if reportlab available
    pdf_out = path + ".report.pdf"
    try:
        write_pdf_report(pdf_out, text)
        print("PDF report written:", pdf_out)
    except Exception:
        print("PDF generation skipped (reportlab not installed or failed). TXT available.")


if __name__ == "__main__":
    main()
