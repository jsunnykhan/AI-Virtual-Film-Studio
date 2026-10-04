from __future__ import annotations

import json
import logging
from typing import Any, Optional

import asyncpg

from agents.core.memory import StudioStore
from db.connection import get_pool
from memory.embeddings import EmbeddingService, get_embedding_service, text_for_entity

logger = logging.getLogger(__name__)


class PostgresVectorStore(StudioStore):
    """
    PostgreSQL vector database store implementing the StudioStore interface.
    Uses pgvector for semantic vector similarity search, alongside robust relational storage
    for projects, canon entities, agent history, and tasks.
    """

    def __init__(
        self,
        embedding_service: Optional[EmbeddingService] = None,
    ) -> None:
        self.embedding_service = embedding_service or get_embedding_service()

    async def _get_pool(self) -> asyncpg.Pool:
        return await get_pool()

    # =========================================================================
    # PROJECT SUMMARY
    # =========================================================================

    async def get_project_summary(self, project_id: str) -> str | None:
        """Retrieve project summary from projects table, or fallback to canon metadata."""
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT summary FROM projects WHERE project_id = $1",
                project_id,
            )
            if row and row["summary"]:
                return row["summary"]

            # Fallback: check if stored in canon_entities
            canon_row = await conn.fetchrow(
                """
                SELECT data FROM canon_entities
                WHERE project_id = $1 AND entity_type IN ('project', 'project_summary', 'concept')
                LIMIT 1
                """,
                project_id,
            )
            if canon_row:
                data = canon_row["data"]
                if isinstance(data, dict):
                    return (
                        data.get("summary")
                        or data.get("series_premise")
                        or data.get("logline")
                        or data.get("premise")
                    )

            return None

    async def upsert_project(
        self,
        project_id: str,
        summary: str,
        name: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Insert or update a project record."""
        pool = await self._get_pool()
        meta_json = json.dumps(metadata or {})
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO projects (project_id, name, summary, metadata, created_at, updated_at)
                VALUES ($1, $2, $3, $4::jsonb, NOW(), NOW())
                ON CONFLICT (project_id) DO UPDATE SET
                    name = COALESCE(EXCLUDED.name, projects.name),
                    summary = EXCLUDED.summary,
                    metadata = EXCLUDED.metadata,
                    updated_at = NOW();
                """,
                project_id,
                name or project_id,
                summary,
                meta_json,
            )
        return {
            "project_id": project_id,
            "name": name or project_id,
            "summary": summary,
            "metadata": metadata or {},
        }

    # =========================================================================
    # CANON RETRIEVAL
    # =========================================================================

    async def get_canon(
        self, project_id: str, entity_ids: list[str]
    ) -> list[dict[str, Any]]:
        """Retrieve multiple canonical entities by their IDs."""
        if not entity_ids:
            return []

        pool = await self._get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT entity_id, entity_type, data
                FROM canon_entities
                WHERE project_id = $1 AND entity_id = ANY($2::text[])
                """,
                project_id,
                entity_ids,
            )

            # Preserve ID lookup mapping
            found = {
                row["entity_id"]: {
                    "id": row["entity_id"],
                    "type": row["entity_type"],
                    "data": (
                        row["data"]
                        if isinstance(row["data"], dict)
                        else json.loads(row["data"])
                    ),
                }
                for row in rows
            }
            return [found[eid] for eid in entity_ids if eid in found]

    async def get_canon_entity(
        self, project_id: str, entity_id: str, entity_type: str
    ) -> dict[str, Any] | None:
        """Retrieve a specific canonical entity matching entity_id and entity_type."""
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT entity_id, entity_type, data
                FROM canon_entities
                WHERE project_id = $1 AND entity_id = $2 AND entity_type = $3
                """,
                project_id,
                entity_id,
                entity_type,
            )
            if row is None:
                return None

            data = (
                row["data"]
                if isinstance(row["data"], dict)
                else json.loads(row["data"])
            )
            return {
                "id": row["entity_id"],
                "type": row["entity_type"],
                "data": data,
            }

    # =========================================================================
    # CANON UPSERT & VECTOR INDEXING
    # =========================================================================

    async def upsert_canon(
        self,
        project_id: str,
        entity_id: str,
        entity_type: str,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Upsert a canon entity and automatically generate & store its pgvector embedding.
        """
        pool = await self._get_pool()

        # Build semantic text representation and compute embedding vector
        text_repr = text_for_entity(entity_type, data)
        embedding = self.embedding_service.embed_query(text_repr)

        data_json = json.dumps(data, ensure_ascii=False)

        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO canon_entities (
                    project_id, entity_id, entity_type, data, embedding, created_at, updated_at
                )
                VALUES ($1, $2, $3, $4::jsonb, $5, NOW(), NOW())
                ON CONFLICT (project_id, entity_id) DO UPDATE SET
                    entity_type = EXCLUDED.entity_type,
                    data = EXCLUDED.data,
                    embedding = EXCLUDED.embedding,
                    updated_at = NOW();
                """,
                project_id,
                entity_id,
                entity_type,
                data_json,
                embedding,
            )

        return {
            "id": entity_id,
            "type": entity_type,
            "data": data,
        }

    # =========================================================================
    # SEMANTIC VECTOR SEARCH
    # =========================================================================

    async def search_canon(
        self,
        project_id: str,
        query: str,
        limit: int = 10,
        entity_type: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Search canonical records using pgvector cosine similarity.
        Falls back to keyword matching if vector search yields no matches.
        """
        q = query.strip()
        if not q:
            return []

        pool = await self._get_pool()
        query_embedding = self.embedding_service.embed_query(q)

        async with pool.acquire() as conn:
            # 1. Primary vector similarity search via pgvector cosine distance (<=>)
            rows = await conn.fetch(
                """
                SELECT entity_id, entity_type, data,
                       1 - (embedding <=> $3) AS similarity
                FROM canon_entities
                WHERE project_id = $1
                  AND ($2::text IS NULL OR entity_type = $2)
                  AND embedding IS NOT NULL
                ORDER BY embedding <=> $3 ASC
                LIMIT $4;
                """,
                project_id,
                entity_type,
                query_embedding,
                limit,
            )

            results: list[dict[str, Any]] = []
            seen_ids = set()

            for row in rows:
                seen_ids.add(row["entity_id"])
                data = (
                    row["data"]
                    if isinstance(row["data"], dict)
                    else json.loads(row["data"])
                )
                results.append(
                    {
                        "id": row["entity_id"],
                        "type": row["entity_type"],
                        "data": data,
                        "score": round(float(row["similarity"]), 4),
                    }
                )

            # 2. Hybrid fallback: If fewer than limit results, search for exact text/substring matches
            if len(results) < limit:
                remaining = limit - len(results)
                keyword_pattern = f"%{q}%"
                text_rows = await conn.fetch(
                    """
                    SELECT entity_id, entity_type, data
                    FROM canon_entities
                    WHERE project_id = $1
                      AND ($2::text IS NULL OR entity_type = $2)
                      AND (
                          entity_id ILIKE $3
                          OR data::text ILIKE $3
                      )
                      AND entity_id != ALL($4::text[])
                    LIMIT $5;
                    """,
                    project_id,
                    entity_type,
                    keyword_pattern,
                    list(seen_ids) if seen_ids else [""],
                    remaining,
                )

                for row in text_rows:
                    data = (
                        row["data"]
                        if isinstance(row["data"], dict)
                        else json.loads(row["data"])
                    )
                    results.append(
                        {
                            "id": row["entity_id"],
                            "type": row["entity_type"],
                            "data": data,
                            "score": 1.0,
                        }
                    )

            return results

    # =========================================================================
    # AGENT HISTORY & RUNS
    # =========================================================================

    async def get_recent_history(
        self, project_id: str, agent_id: str, limit: int = 5
    ) -> list[dict[str, Any]]:
        """Retrieve recent run outputs for an agent in chronological order."""
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT project_id, agent_id, task_id, result
                FROM (
                    SELECT project_id, agent_id, task_id, result, created_at
                    FROM agent_runs
                    WHERE project_id = $1 AND agent_id = $2
                    ORDER BY created_at DESC
                    LIMIT $3
                ) sub
                ORDER BY created_at ASC;
                """,
                project_id,
                agent_id,
                limit,
            )

            return [
                {
                    "project_id": row["project_id"],
                    "agent_id": row["agent_id"],
                    "task_id": row["task_id"],
                    "result": (
                        row["result"]
                        if isinstance(row["result"], dict)
                        else json.loads(row["result"])
                    ),
                }
                for row in rows
            ]

    async def save_result(
        self,
        project_id: str,
        agent_id: str,
        task_id: str,
        result: dict[str, Any],
    ) -> None:
        """Persist an agent execution result."""
        pool = await self._get_pool()
        result_json = json.dumps(result, ensure_ascii=False)
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO agent_runs (project_id, agent_id, task_id, result, created_at)
                VALUES ($1, $2, $3, $4::jsonb, NOW());
                """,
                project_id,
                agent_id,
                task_id,
                result_json,
            )

    # =========================================================================
    # TASK MANAGEMENT
    # =========================================================================

    async def create_task(self, task: dict[str, Any]) -> dict[str, Any]:
        """Create or update a workflow task record."""
        pool = await self._get_pool()
        task_id = str(task["task_id"])
        project_id = str(task.get("project_id", ""))
        agent_id = str(task.get("agent_id", ""))
        objective = str(task.get("objective", ""))
        status = str(task.get("status", "pending"))
        data_json = json.dumps(task, ensure_ascii=False)

        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO tasks (
                    task_id, project_id, agent_id, objective, status, data, created_at, updated_at
                )
                VALUES ($1, $2, $3, $4, $5, $6::jsonb, NOW(), NOW())
                ON CONFLICT (task_id) DO UPDATE SET
                    project_id = EXCLUDED.project_id,
                    agent_id = EXCLUDED.agent_id,
                    objective = EXCLUDED.objective,
                    status = EXCLUDED.status,
                    data = EXCLUDED.data,
                    updated_at = NOW();
                """,
                task_id,
                project_id,
                agent_id,
                objective,
                status,
                data_json,
            )

        return dict(task)

    async def get_task(self, task_id: str) -> dict[str, Any] | None:
        """Get a task record by its task_id."""
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT data FROM tasks WHERE task_id = $1",
                task_id,
            )
            if row is None:
                return None
            return (
                row["data"]
                if isinstance(row["data"], dict)
                else json.loads(row["data"])
            )

    # =========================================================================
    # UTILITIES
    # =========================================================================

    async def delete_canon(self, project_id: str, entity_id: str) -> bool:
        """Delete a canonical entity."""
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            result = await conn.execute(
                "DELETE FROM canon_entities WHERE project_id = $1 AND entity_id = $2",
                project_id,
                entity_id,
            )
            return "DELETE 1" in result

    async def clear(self, project_id: str | None = None) -> None:
        """Clear database records for a project or all projects (useful in tests)."""
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            if project_id:
                await conn.execute(
                    "DELETE FROM canon_entities WHERE project_id = $1", project_id
                )
                await conn.execute(
                    "DELETE FROM agent_runs WHERE project_id = $1", project_id
                )
                await conn.execute(
                    "DELETE FROM tasks WHERE project_id = $1", project_id
                )
                await conn.execute(
                    "DELETE FROM projects WHERE project_id = $1", project_id
                )
            else:
                await conn.execute("TRUNCATE canon_entities, agent_runs, tasks, projects;")
