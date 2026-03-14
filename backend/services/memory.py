"""
Per-user persistent memory using ChromaDB vector embeddings.

Stores past design prompts, results, and refinements as embeddings
so the system can reference prior work and suggest improvements.
"""

import chromadb
from chromadb.config import Settings as ChromaSettings
from config import settings

_client = None
_collection = None


def get_collection():
    global _client, _collection
    if _collection is None:
        _client = chromadb.Client(ChromaSettings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=settings.CHROMA_PERSIST_DIR,
            anonymized_telemetry=False,
        ))
        _collection = _client.get_or_create_collection(
            name="design_memory",
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


def store_design_memory(user_id: str, design_id: str, prompt: str, summary: str):
    """Store a design in the user's memory for future reference."""
    collection = get_collection()
    doc_id = f"{user_id}_{design_id}"
    collection.upsert(
        ids=[doc_id],
        documents=[f"Prompt: {prompt}\n\nResult: {summary}"],
        metadatas=[{"user_id": user_id, "design_id": design_id}],
    )


def recall_similar_designs(user_id: str, query: str, n_results: int = 3) -> list[dict]:
    """Find past designs similar to the current query."""
    collection = get_collection()

    try:
        results = collection.query(
            query_texts=[query],
            n_results=n_results,
            where={"user_id": user_id},
        )
    except Exception:
        return []

    memories = []
    if results and results.get("documents"):
        for i, doc in enumerate(results["documents"][0]):
            memories.append({
                "content": doc,
                "design_id": results["metadatas"][0][i].get("design_id", ""),
                "distance": results["distances"][0][i] if results.get("distances") else None,
            })

    return memories
