from datetime import datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field


class AgentTask(BaseModel):
    """
    A single task sent to an agent.
    """

    model_config = ConfigDict(extra="forbid")
    task_id: str
    project_id: str
    agent_id: str
    objective: str
    scene_id: str | None = None
    character_ids: list[str] = Field(default_factory=list)
    asset_ids: list[str] = Field(default_factory=list)
    input_data: dict[str, Any] = Field(default_factory=dict)
    priority: int = Field(default=5, ge=1, le=10)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AgentContext(BaseModel):
    """
    The compact context assembled specifically for an LLM call.
    """

    model_config = ConfigDict(extra="forbid")
    system_rules: str
    role_instructions: str
    project_summary: str | None = None
    relevant_canon: list[dict[str, Any]] = Field(default_factory=list)
    relevant_history: list[dict[str, Any]] = Field(default_factory=list)
    current_task: dict[str, Any] = Field(default_factory=dict)
    constraints: list[str] = Field(default_factory=list)


class AgentDecision(BaseModel):
    """
    Result of an agent's reasoning/decision.
    This is intentionally much smaller than storing raw reasoning.
    """

    decision: str
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    assumptions: list[str] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)


T = TypeVar("T", bound=BaseModel)


class AgentResult(BaseModel, Generic[T]):
    """
    Standard result returned by every agent.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)
    task_id: str
    agent_id: str
    success: bool
    output: T | None = None
    decision: AgentDecision | None = None
    errors: list[str] = Field(default_factory=list)
    input_tokens: int = 0
    output_tokens: int = 0
    latency_ms: int = 0
    model: str | None = None
