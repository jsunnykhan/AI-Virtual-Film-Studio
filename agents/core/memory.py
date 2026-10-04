from abc import ABC, abstractmethod
from typing import Any


class MemoryStore(ABC):
    """
    Abstract interface for agent/project memory.
    """

    @abstractmethod
    async def get_project_summary(
        self,
        project_id: str,
    ) -> str | None: ...

    @abstractmethod
    async def get_canon(
        self,
        project_id: str,
        entity_ids: list[str],
    ) -> list[dict[str, Any]]: ...

    @abstractmethod
    async def get_recent_history(
        self,
        project_id: str,
        agent_id: str,
        limit: int = 5,
    ) -> list[dict[str, Any]]: ...

    @abstractmethod
    async def save_result(
        self,
        project_id: str,
        agent_id: str,
        task_id: str,
        result: dict[str, Any],
    ) -> None: ...


class InMemoryStore(MemoryStore):

    def __init__(self) -> None:
        self.projects: dict[str, dict[str, Any]] = {}
        self.results: list[dict[str, Any]] = []

    async def get_project_summary(
        self,
        project_id: str,
    ) -> str | None:

        project = self.projects.get(project_id)

        if not project:
            return None

        return project.get("summary")

    async def get_canon(
        self,
        project_id: str,
        entity_ids: list[str],
    ) -> list[dict[str, Any]]:

        project = self.projects.get(project_id, {})

        entities = project.get("canon", [])

        if not entity_ids:
            return entities

        return [entity for entity in entities if entity.get("id") in entity_ids]

    async def get_recent_history(
        self,
        project_id: str,
        agent_id: str,
        limit: int = 5,
    ) -> list[dict[str, Any]]:

        results = [
            item
            for item in self.results
            if item["project_id"] == project_id and item["agent_id"] == agent_id
        ]

        return results[-limit:]

    async def save_result(
        self,
        project_id: str,
        agent_id: str,
        task_id: str,
        result: dict[str, Any],
    ) -> None:

        self.results.append(
            {
                "project_id": project_id,
                "agent_id": agent_id,
                "task_id": task_id,
                "result": result,
            }
        )
