"""
Vector database setup for Stage 1 (Vector Similarity) detection.
Uses ChromaDB in "persistent" mode — data is saved to disk in the
chroma_data/ folder, so the known-attack corpus survives app restarts.
"""

import chromadb

_client = chromadb.PersistentClient(path="chroma_data")

# ChromaDB's built-in embedding model runs locally — no API key needed.
_collection = _client.get_or_create_collection(name="known_attacks")


def get_collection():
    return _collection