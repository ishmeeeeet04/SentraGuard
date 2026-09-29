"""
Tests for Stage 0 (Pre-Filter) — the fastest, cheapest detection layer.
These tests need no database or network access, so they run instantly.
"""

from app.detection.prefilter import run_prefilter
from app.detection.models import Verdict


def test_prefilter_blocks_aws_key():
    result = run_prefilter("My AWS key is AKIAABCDEFGHIJKLMNOP")
    assert result.verdict == Verdict.BLOCK
    assert "AWS" in result.reason


def test_prefilter_blocks_email_pii():
    result = run_prefilter("Please contact me at john.doe@example.com")
    assert result.verdict == Verdict.BLOCK


def test_prefilter_allows_safe_text():
    result = run_prefilter("What is the capital of France?")
    assert result.verdict == Verdict.SAFE