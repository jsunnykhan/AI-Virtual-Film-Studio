from agents.core.states import CreativeWorkflowState
from agents.core.schemas import AgentTask

from agents.agent_container import (
    idea_generator,
    idea_critic,
    concept_developer,
)

## ============================================================
# NODES
## ============================================================


async def idea_generator_node(state: CreativeWorkflowState):
    """
    Node for generating ideas.
    """
    task = AgentTask(
        task_id=state.get("task_id", ""),
        project_id=state.get("project_id", ""),
        agent_id="idea_generator",
        objective=(
            "Autonomously generate an original animated series or movie concept. "
            "Choose the format, genre, and story without requiring a user prompt."
        ),
        input_data={
            "iteration": state.get("iteration", 0),
            "max_iterations": state.get("max_iterations", 3),
            "ideas": state.get("ideas", []),
            "critique": state.get("critique", {}),
            "selected_idea": state.get("selected_idea"),
            "concept": state.get("concept"),
            "status": state.get("status", ""),
            "error": state.get("error"),
        },
    )

    result = await idea_generator.run(task)
    return {
        "idea": result.model_dump(),
        "status": "idea_generated",
    }


async def idea_critic_node(
    state: CreativeWorkflowState,
):
    task = AgentTask(
        task_id=state.get("task_id", ""),
        project_id=state.get("project_id", ""),
        agent_id="idea_critic",
        objective="Evaluate the generated animated-series concept",
        input_data={
            "user_request": state.get("user_request", ""),
            "idea": state.get("idea"),
            "iteration": state.get("iteration", 0),
        },
    )

    result = await idea_critic.run(task)

    return {
        "critique": result.model_dump(),
        "status": "idea_criticized",
    }


async def concept_developer_node(
    state: CreativeWorkflowState,
):
    task = AgentTask(
        task_id=state.get("task_id", ""),
        project_id=state.get("project_id", ""),
        agent_id="concept_developer",
        objective="Develop the approved idea into a complete series concept",
        input_data={
            "user_request": state.get("user_request", ""),
            "idea": state.get("idea"),
            "critique": state.get("critique", {}),
        },
    )

    result = await concept_developer.run(task)

    print(f"Concept Developer Result: {result.model_dump()}")

    return {
        "concept": result.model_dump(),
        "status": "concept_developed",
    }
