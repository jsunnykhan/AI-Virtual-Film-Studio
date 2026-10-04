import json
import time
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

import litellm
from pydantic import BaseModel

from agents.core.context import ContextManager
from agents.core.memory import StudioStore
from agents.core.policies import AgentPolicy, PolicyEngine
from agents.core.schemas import (
    AgentContext,
    AgentResult,
    AgentTask,
)

from shared.core.settings import Settings

OutputT = TypeVar("OutputT", bound=BaseModel)

settings = Settings()
litellm.api_key = settings.openai_api_key
litellm.api_base = settings.openai_base_url


class BaseAgent(ABC, Generic[OutputT]):
    """
    Shared runtime for every AI Studio agent.

    Example:
        class DirectorAgent(BaseAgent[DirectorOutput]):
            ...
    """

    def __init__(
        self,
        *,
        memory: StudioStore,
        context_manager: ContextManager,
        policy: AgentPolicy,
        policy_engine: PolicyEngine,
    ) -> None:

        self.memory = memory
        self.context_manager = context_manager
        self.policy = policy
        self.policy_engine = policy_engine

    @property
    @abstractmethod
    def agent_id(self) -> str:
        """Unique agent name."""
        ...

    @property
    @abstractmethod
    def role_instructions(self) -> str:
        """Agent-specific system prompt."""
        ...

    @property
    @abstractmethod
    def output_schema(self) -> type[OutputT]:
        """Pydantic schema expected from the LLM."""
        ...

    def studio_rules(self) -> str:
        return """
            You are an AI agent inside a professional film production studio.

            Global rules:

            1. Stay inside your assigned role.
            2. Follow the approved Movie Bible.
            3. Never silently contradict approved canon.
            4. Never invent unknown project facts as if they were approved.
            5. Produce structured outputs.
            6. Preserve continuity.
            7. Do not expose private chain-of-thought.
            8. Return concise decisions, evidence and artifacts.
        """

    async def run(
        self,
        task: AgentTask,
    ) -> AgentResult[OutputT]:

        started_at = time.perf_counter()

        try:
            # --------------------------------------------------
            # 1. Validate agent policy
            # --------------------------------------------------

            self.policy_engine.validate_task(
                self.policy,
                task.agent_id,
            )

            # --------------------------------------------------
            # 2. Build minimal context
            # --------------------------------------------------

            context = await self.context_manager.build(
                task=task,
                policy=self.policy,
                role_instructions=self.role_instructions,
                system_rules=self.studio_rules(),
            )

            # --------------------------------------------------
            # 3. Call LLM
            # --------------------------------------------------

            raw_response = await self._call_llm(context)

            # --------------------------------------------------
            # 4. Parse / validate structured output
            # --------------------------------------------------

            output = self._parse_output(raw_response)

            # --------------------------------------------------
            # 5. Persist useful result
            # --------------------------------------------------

            await self.memory.save_result(
                project_id=task.project_id,
                agent_id=self.agent_id,
                task_id=task.task_id,
                result=output.model_dump(),
            )

            latency_ms = int((time.perf_counter() - started_at) * 1000)

            usage = raw_response.get("usage", {})

            return AgentResult(
                task_id=task.task_id,
                agent_id=self.agent_id,
                success=True,
                output=output,
                input_tokens=usage.get(
                    "prompt_tokens",
                    0,
                ),
                output_tokens=usage.get(
                    "completion_tokens",
                    0,
                ),
                latency_ms=latency_ms,
                model=self.policy.model,
            )

        except Exception as exc:

            latency_ms = int((time.perf_counter() - started_at) * 1000)

            return AgentResult(
                task_id=task.task_id,
                agent_id=self.agent_id,
                success=False,
                errors=[str(exc)],
                latency_ms=latency_ms,
                model=self.policy.model,
            )

    async def _call_llm(
        self,
        context: AgentContext,
    ) -> dict:

        system_prompt = self._build_system_prompt(context)

        user_prompt = self._build_user_prompt(context)

        response = await litellm.acompletion(
            model=self.policy.model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            temperature=self.policy.temperature,
            max_tokens=self.policy.max_output_tokens,
        )

        content = response.choices[0].message.content  # type: ignore

        if not content:
            raise ValueError("LLM returned empty response.")

        return {
            "content": content,
            "usage": (response.usage.model_dump() if response.usage else {}),  # type: ignore
        }

    def _build_system_prompt(
        self,
        context: AgentContext,
    ) -> str:

        schema = json.dumps(
            self.output_schema.model_json_schema(),
            indent=2,
        )

        return f"""
                {context.system_rules}

                ROLE
                {context.role_instructions}

                OUTPUT REQUIREMENTS

                Return ONLY valid JSON.

                Your JSON must conform to this schema:

                {schema}
            """

    def _build_user_prompt(
        self,
        context: AgentContext,
    ) -> str:

        payload = {
            "project_summary": context.project_summary,
            "relevant_canon": context.relevant_canon,
            "relevant_history": context.relevant_history,
            "current_task": context.current_task,
            "constraints": context.constraints,
        }

        return json.dumps(
            payload,
            ensure_ascii=False,
        )

    def _parse_output(
        self,
        raw_response: dict,
    ) -> OutputT:

        content = raw_response["content"]

        try:
            data = json.loads(content)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON from model: {exc}") from exc

        return self.output_schema.model_validate(data)
