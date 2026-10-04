from __future__ import annotations

from typing import Optional
from memory.postgres_vector import PostgresVectorStore

_vector_store: Optional[PostgresVectorStore] = None


def get_vector_store() -> PostgresVectorStore:
    """Return a singleton instance of PostgresVectorStore."""
    global _vector_store
    if _vector_store is None:
        _vector_store = PostgresVectorStore()
    return _vector_store


__all__ = ["PostgresVectorStore", "get_vector_store"]
