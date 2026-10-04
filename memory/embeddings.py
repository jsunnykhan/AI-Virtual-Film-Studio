from __future__ import annotations

import json
import logging
import math
from typing import Any, Optional

from shared.core.settings import get_settings

logger = logging.getLogger(__name__)


def text_for_entity(entity_type: str, data: dict[str, Any]) -> str:
    """Build a semantically rich textual representation of a canonical entity."""
    parts = [f"Entity Type: {entity_type}"]
    for key, val in data.items():
        if val is None:
            continue
        if isinstance(val, (str, int, float, bool)):
            parts.append(f"{key}: {val}")
        elif isinstance(val, list):
            if all(isinstance(x, str) for x in val):
                parts.append(f"{key}: {', '.join(val)}")
            elif all(isinstance(x, dict) for x in val):
                parts.append(f"{key}: {json.dumps(val, ensure_ascii=False)}")
            else:
                parts.append(f"{key}: {val}")
        elif isinstance(val, dict):
            parts.append(f"{key}: {json.dumps(val, ensure_ascii=False)}")
    if len(parts) == 1:
        return f"Entity Type: {entity_type}\n{json.dumps(data, ensure_ascii=False)}"
    return "\n".join(parts)


class EmbeddingService:
    """Embedding service using fastembed (local ONNX) with graceful resilience."""

    def __init__(self, model_name: str | None = None, dim: int | None = None) -> None:
        settings = get_settings()
        self.model_name = model_name or settings.embedding_model
        self.dim = dim or settings.embedding_dim
        self._model = None

    def _get_model(self):
        if self._model is None:
            try:
                from fastembed import TextEmbedding
                self._model = TextEmbedding(model_name=self.model_name)
            except Exception as e:
                logger.warning(
                    f"Could not initialize FastEmbed model '{self.model_name}': {e}. "
                    "Falling back to deterministic embeddings."
                )
                self._model = False
        return self._model

    def _fallback_embedding(self, text: str) -> list[float]:
        """Deterministic normalized dense embedding vector if local model unavailable."""
        import hashlib
        dim = self.dim
        vec = [0.0] * dim
        words = text.lower().split()
        if not words:
            return vec

        for w in words:
            h = int(hashlib.sha256(w.encode("utf-8")).hexdigest(), 16)
            idx = h % dim
            sign = 1.0 if ((h >> 32) & 1) else -1.0
            vec[idx] += sign * 1.0

        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            vec = [x / norm for x in vec]
        return vec

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Generate dense embeddings for a list of text strings."""
        if not texts:
            return []

        model = self._get_model()
        if model:
            try:
                results = list(model.embed(texts))
                return [list(r) for r in results]
            except Exception as exc:
                logger.error(f"Error generating fastembed embeddings: {exc}")

        return [self._fallback_embedding(t) for t in texts]

    def embed_query(self, text: str) -> list[float]:
        """Generate dense embedding for a single search query."""
        results = self.embed_documents([text])
        return results[0] if results else [0.0] * self.dim


_embedding_service: Optional[EmbeddingService] = None


def get_embedding_service() -> EmbeddingService:
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
