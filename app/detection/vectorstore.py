"""
Vector database setup for Stage 1 (Vector Similarity) detection.
Uses ChromaDB in "persistent" mode — data is saved to disk in the
chroma_data/ folder, so the known-attack corpus survives app restarts.

We explicitly configure the collection to use cosine similarity, so
scores are directly interpretable: 1.0 = identical meaning, 0.0 = totally
unrelated.
"""

import chromadb

_client = chromadb.PersistentClient(path="chroma_data")

_collection = _client.get_or_create_collection(
    name="known_attacks",
    metadata={"hnsw:space": "cosine"},
)


def get_collection():
    return _collection