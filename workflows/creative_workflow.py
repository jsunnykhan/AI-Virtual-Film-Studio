from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from agents.core.states import CreativeWorkflowState

from workflows.nodes import (
    idea_generator_node,
    idea_critic_node,
    concept_developer_node,
)

# ============================================================
# ROUTER
# ============================================================


def route_after_critic(
    state: CreativeWorkflowState,
) -> str:

    critique = state.get("critique", {})

    print(f"Critique: {critique}")

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

    graph.add_node("idea_generator", idea_generator_node)

    graph.add_node("idea_critic", idea_critic_node)

    graph.add_node("concept_developer", concept_developer_node)

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

    return graph.compile()
