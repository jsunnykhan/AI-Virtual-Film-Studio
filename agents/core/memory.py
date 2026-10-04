from abc import ABC, abstractmethod
from typing import Any


class StudioStore(ABC):
    @abstractmethod
    async def get_project_summary(self, project_id: str) -> str | None: ...

    @abstractmethod
    async def get_canon(
        self, project_id: str, entity_ids: list[str]
    ) -> list[dict[str, Any]]: ...

    @abstractmethod
    async def get_canon_entity(
        self, project_id: str, entity_id: str, entity_type: str
    ) -> dict[str, Any] | None: ...

    @abstractmethod
    async def search_canon(
        self,
        project_id: str,
        query: str,
        limit: int = 10,
        entity_type: str | None = None,
    ) -> list[dict[str, Any]]: ...

    @abstractmethod
    async def get_recent_history(
        self, project_id: str, agent_id: str, limit: int = 5
    ) -> list[dict[str, Any]]: ...

    @abstractmethod
    async def save_result(
        self, project_id: str, agent_id: str, task_id: str, result: dict[str, Any]
    ) -> None: ...

    @abstractmethod
    async def create_task(self, task: dict[str, Any]) -> dict[str, Any]: ...

    @abstractmethod
    async def get_task(self, task_id: str) -> dict[str, Any] | None: ...

    @abstractmethod
    async def upsert_canon(
        self,
        project_id: str,
        entity_id: str,
        entity_type: str,
        data: dict[str, Any],
    ) -> dict[str, Any]: ...
