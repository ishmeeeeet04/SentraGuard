"""
One-time script: loads the known-attack corpus into ChromaDB.
Run this once now, and again any time KNOWN_ATTACKS is updated.

Usage (from the project root, with venv active):
    python -m scripts.seed_vectorstore
"""

from app.detection.vectorstore import get_collection
from app.detection.known_attacks import KNOWN_ATTACKS


def seed():
    collection = get_collection()
    collection.upsert(
        ids=[a["id"] for a in KNOWN_ATTACKS],
        documents=[a["text"] for a in KNOWN_ATTACKS],
    )
    print(f"Seeded {len(KNOWN_ATTACKS)} known attack patterns into the vector store.")


if __name__ == "__main__":
    seed()