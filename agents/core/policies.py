from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class AgentPolicy:
    """
    Defines what an agent can do and how much it is allowed to consume.
    """

    agent_id: str
    model: str
    max_input_tokens: int = 8_000
    max_output_tokens: int = 2_000
    temperature: float = 0.2
    allowed_tools: tuple[str, ...] = field(default_factory=tuple)
    max_retries: int = 2
    require_structured_output: bool = True


class PolicyViolation(Exception):
    """Raised when an agent tries to break its policy."""


class PolicyEngine:
    """
    Central policy checker.
    """

    def validate_task(
        self,
        policy: AgentPolicy,
        task_agent_id: str,
    ) -> None:

        if policy.agent_id != task_agent_id:
            raise PolicyViolation(
                f"Task agent '{task_agent_id}' does not match "
                f"policy agent '{policy.agent_id}'."
            )

    def validate_tool(
        self,
        policy: AgentPolicy,
        tool_name: str,
    ) -> None:

        if tool_name not in policy.allowed_tools:
            raise PolicyViolation(
                f"Agent '{policy.agent_id}' is not allowed "
                f"to use tool '{tool_name}'."
            )

    def validate_token_budget(
        self,
        policy: AgentPolicy,
        estimated_tokens: int,
    ) -> None:

        if estimated_tokens > policy.max_input_tokens:
            raise PolicyViolation(
                f"Context requires approximately "
                f"{estimated_tokens} tokens, but policy allows "
                f"{policy.max_input_tokens}."
            )
