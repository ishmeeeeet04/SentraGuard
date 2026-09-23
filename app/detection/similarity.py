"""
Stage 1: Vector Similarity.
Embeds the incoming prompt and compares it against the known-attack
corpus in ChromaDB. High similarity to a known attack means the new
prompt likely carries the same malicious intent, even with different
wording.
"""

from app.detection.models import DetectionResult, Verdict
from app.detection.vectorstore import get_collection

# Thresholds — tunable. These are starting points, not final values;
# Module 5 (Hardening) is where we'll tune these against real benchmarks.
BLOCK_THRESHOLD = 0.80
SUSPICIOUS_THRESHOLD = 0.50


def run_similarity_check(text: str) -> DetectionResult:
    collection = get_collection()

    results = collection.query(query_texts=[text], n_results=1)

    # No patterns in the corpus at all (shouldn't happen once seeded).
    if not results["distances"] or not results["distances"][0]:
        return DetectionResult(
            stage="vector_similarity",
            verdict=Verdict.SAFE,
            confidence=0.0,
            reason="No known attack patterns to compare against",
        )

    distance = results["distances"][0][0]
    matched_text = results["documents"][0][0]

    # With cosine space, ChromaDB's "distance" is (1 - cosine_similarity).
    similarity = 1 - distance

    if similarity >= BLOCK_THRESHOLD:
        verdict = Verdict.BLOCK
    elif similarity >= SUSPICIOUS_THRESHOLD:
        verdict = Verdict.SUSPICIOUS
    else:
        verdict = Verdict.SAFE

    return DetectionResult(
        stage="vector_similarity",
        verdict=verdict,
        confidence=round(similarity, 3),
        reason=f"Closest match ({similarity:.2f} similarity): \"{matched_text}\"",
    )