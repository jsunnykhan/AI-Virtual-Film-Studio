from typing import Any, TypedDict


class CreativeWorkflowState(TypedDict, total=False):
    project_id: str
    workflow_id: str
    task_id: str
    user_request: str
    ideas: list[dict[str, Any]]
    critique: dict[str, Any]
    selected_idea: dict[str, Any] | None
    concept: dict[str, Any] | None
    iteration: int
    max_iterations: int
    status: str
    error: str | None
