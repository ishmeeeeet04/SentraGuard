"""
Shared data shapes used across every detection pipeline stage
(pre-filter, vector similarity, classifier, LLM-judge).
Every stage returns a DetectionResult, so the orchestrator (LangGraph,
built in Step 4) can treat all stages identically.
"""

from dataclasses import dataclass
from enum import Enum


class Verdict(str, Enum):
    SAFE = "safe"           # this stage found nothing suspicious
    SUSPICIOUS = "suspicious"  # ambiguous — pass to the next stage
    BLOCK = "block"          # confident this is malicious/sensitive


@dataclass
class DetectionResult:
    stage: str
    verdict: Verdict
    confidence: float  # 0.0 to 1.0
    reason: str