from agents.core.memory import StudioStore
from agents.core.policies import AgentPolicy
from agents.core.schemas import AgentContext, AgentTask


class ContextManager:

    def __init__(self, memory: StudioStore) -> None:
        self.memory = memory

    async def build(
        self,
        task: AgentTask,
        policy: AgentPolicy,
        role_instructions: str,
        system_rules: str,
    ) -> AgentContext:

        project_summary = await self.memory.get_project_summary(task.project_id)

        # Only retrieve explicitly relevant entities.
        entity_ids = [
            *task.character_ids,
            *task.asset_ids,
        ]

        relevant_canon = await self.memory.get_canon(
            project_id=task.project_id,
            entity_ids=entity_ids,
        )

        # Don't send the entire agent history.
        history = await self.memory.get_recent_history(
            project_id=task.project_id,
            agent_id=task.agent_id,
            limit=3,
        )

        return AgentContext(
            system_rules=system_rules,
            role_instructions=role_instructions,
            project_summary=project_summary,
            relevant_canon=relevant_canon,
            relevant_history=history,
            current_task={
                "task_id": task.task_id,
                "objective": task.objective,
                "scene_id": task.scene_id,
                "input_data": task.input_data,
            },
            constraints=[
                f"maximum output tokens: {policy.max_output_tokens}",
            ],
        )
