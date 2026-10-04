from typing import Any
from agents.core.memory import StudioStore


class InMemoryStore(StudioStore):
    def __init__(self) -> None:
        self.projects: dict[str, dict[str, Any]] = {}
        self.canon: dict[tuple[str, str], dict[str, Any]] = {}
        self.agent_runs: list[dict[str, Any]] = []
        self.tasks: dict[str, dict[str, Any]] = {}

    async def get_project_summary(self, project_id: str) -> str | None:
        project = self.projects.get(project_id)
        return project.get("summary") if project else None

    async def get_canon(
        self, project_id: str, entity_ids: list[str]
    ) -> list[dict[str, Any]]:
        if not entity_ids:
            return []
        return [
            self.canon[(project_id, entity_id)]
            for entity_id in entity_ids
            if (project_id, entity_id) in self.canon
        ]

    async def get_canon_entity(
        self, project_id: str, entity_id: str, entity_type: str
    ) -> dict[str, Any] | None:
        item = self.canon.get((project_id, entity_id))
        if item is None or item["type"] != entity_type:
            return None
        return item

    async def search_canon(
        self,
        project_id: str,
        query: str,
        limit: int = 10,
        entity_type: str | None = None,
    ) -> list[dict[str, Any]]:
        q = query.strip().lower()
        if not q:
            return []
        results: list[dict[str, Any]] = []
        for (pid, _), item in self.canon.items():
            if pid != project_id:
                continue
            if entity_type and item["type"] != entity_type:
                continue
            if q in str(item["data"]).lower():
                results.append(item)
            if len(results) >= limit:
                break
        return results

    async def get_recent_history(
        self, project_id: str, agent_id: str, limit: int = 5
    ) -> list[dict[str, Any]]:
        rows = [
            row
            for row in self.agent_runs
            if row["project_id"] == project_id and row["agent_id"] == agent_id
        ]
        return rows[-limit:]

    async def save_result(
        self, project_id: str, agent_id: str, task_id: str, result: dict[str, Any]
    ) -> None:
        self.agent_runs.append(
            {
                "project_id": project_id,
                "agent_id": agent_id,
                "task_id": task_id,
                "result": result,
            }
        )

    async def create_task(self, task: dict[str, Any]) -> dict[str, Any]:
        self.tasks[task["task_id"]] = dict(task)
        return self.tasks[task["task_id"]]

    async def get_task(self, task_id: str) -> dict[str, Any] | None:
        return self.tasks.get(task_id)

    async def upsert_canon(
        self,
        project_id: str,
        entity_id: str,
        entity_type: str,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        value = {"id": entity_id, "type": entity_type, "data": data}
        self.canon[(project_id, entity_id)] = value
        return value
