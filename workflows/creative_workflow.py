from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from agents.core.schemas import AgentTask
from agents.core.states import CreativeWorkflowState

from agents.agent_container import (
    idea_generator,
    idea_critic,
    concept_developer,
)


from typing import Any, TypedDict


# ============================================================
# State
# ============================================================
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


# ============================================================
# IDEA GENERATOR NODE
# ============================================================


async def idea_generator_node(state: CreativeWorkflowState):
    task = AgentTask(
        task_id=state.get("task_id", ""),
        project_id=state.get("project_id", ""),
        agent_id="idea_generator",
        objective="Generate an original animated-series concept",
        input_data={
            "user_request": state.get("user_request", ""),
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


# ============================================================
# IDEA CRITIC NODE
# ============================================================


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


# ============================================================
# CONCEPT DEVELOPER NODE
# ============================================================


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

    return {
        "concept": result.model_dump(),
        "status": "concept_developed",
    }


# ============================================================
# ROUTER
# ============================================================


def route_after_critic(
    state: CreativeWorkflowState,
) -> str:

    critique = state.get("critique", {})

    needs_revision = critique.get(
        "needs_revision",
        False,
    )

    iteration = state.get(
        "iteration",
        0,
    )

    max_iterations = state.get(
        "max_iterations",
        3,
    )

    if needs_revision and iteration < max_iterations:
        return "regenerate"

    return "develop"


# ============================================================
# GRAPH
# ============================================================


def build_creative_workflow():
    graph = StateGraph(CreativeWorkflowState)

    # --------------------------------------------------------
    # Nodes
    # --------------------------------------------------------

    graph.add_node("idea_generator", idea_generator_node)

    graph.add_node(
        "idea_critic",
        idea_critic_node,
    )

    graph.add_node(
        "concept_developer",
        concept_developer_node,
    )

    # --------------------------------------------------------
    # START
    # --------------------------------------------------------

    graph.add_edge(
        START,
        "idea_generator",
    )

    graph.add_edge(
        "idea_generator",
        END,
    )

    # graph.add_conditional_edges(
    #     "idea_critic",
    #     route_after_critic,
    #     {
    #         "regenerate": "idea_generator",
    #         "develop": "concept_developer",
    #     },
    # )

    # graph.add_edge(
    #     "concept_developer",
    #     END,
    # )

    return graph.compile()
