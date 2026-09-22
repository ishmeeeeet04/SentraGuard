"""
Stage 0: Pre-Filter.
Fast, cheap checks that run before anything AI-based: regex patterns for
common secrets (API keys, etc.) and Presidio's NER-based PII detection
(emails, credit cards, phone numbers, etc.).
"""

import re

from presidio_analyzer import AnalyzerEngine

from app.detection.models import DetectionResult, Verdict

_analyzer = AnalyzerEngine()

# Common secret patterns — each is a (name, compiled regex) pair.
_SECRET_PATTERNS = [
    ("AWS Access Key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("Generic API Key", re.compile(r"(?i)(api[_-]?key|secret[_-]?key)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{16,}")),
    ("Private Key Block", re.compile(r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----")),
]

# PII entity types we care about for this project (Presidio supports many more).
_PII_ENTITIES = ["EMAIL_ADDRESS", "CREDIT_CARD", "PHONE_NUMBER", "US_SSN"]


def run_prefilter(text: str) -> DetectionResult:
    # 1. Check hardcoded secret patterns first — cheapest possible check.
    for name, pattern in _SECRET_PATTERNS:
        if pattern.search(text):
            return DetectionResult(
                stage="prefilter",
                verdict=Verdict.BLOCK,
                confidence=0.99,
                reason=f"Matched known secret pattern: {name}",
            )

    # 2. Run Presidio's NER-based PII detection.
    findings = _analyzer.analyze(text=text, entities=_PII_ENTITIES, language="en")
    if findings:
        entity_types = ", ".join(sorted({f.entity_type for f in findings}))
        return DetectionResult(
            stage="prefilter",
            verdict=Verdict.BLOCK,
            confidence=0.9,
            reason=f"Detected sensitive PII: {entity_types}",
        )

    # 3. Nothing obvious found — let the next stage decide.
    return DetectionResult(
        stage="prefilter",
        verdict=Verdict.SAFE,
        confidence=0.0,
        reason="No obvious secrets or PII detected",
    )