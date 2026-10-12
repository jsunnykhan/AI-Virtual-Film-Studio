from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from agents.core.states import CreativeWorkflowState

from workflows.nodes import (
    idea_generator_node,
    idea_critic_node,
    concept_developer_node,
    executive_producer_node,
    research_agent_node,
)

# ============================================================
# ROUTER
# ============================================================


def route_after_critic(
    state: CreativeWorkflowState,
) -> str:
    critique = state.get("critique", {})
    if not critique.get("success", False):
        return "stop"

    output = critique.get("output") or {}
    if output.get("verdict") == "strong_candidate":
        return "develop"

    if state.get("iteration", 0) < state.get("max_iterations", 3):
        return "regenerate"
    return "stop"


def route_after_executive_producer(
    state: CreativeWorkflowState,
) -> str:
    decision = state.get("final_decision", {})
    if not decision.get("success", False):
        return "stop"

    output = decision.get("output") or {}
    if output.get("approved") is True:
        return "critic"

    if state.get("iteration", 0) < state.get("max_iterations", 3):
        return "regenerate"
    return "stop"


def route_after_idea_generator(
    state: CreativeWorkflowState,
) -> str:
    idea = state.get("idea", {})
    return "executive_producer" if idea.get("success", False) else "stop"


# ============================================================
# GRAPH
# ============================================================


def build_creative_workflow():
    graph = StateGraph(CreativeWorkflowState)

    graph.add_node("idea_generator", idea_generator_node)
    graph.add_node("idea_critic", idea_critic_node)
    graph.add_node("concept_developer", concept_developer_node)
    graph.add_node("executive_producer", executive_producer_node)
    graph.add_node("research_agent", research_agent_node)

    # --------------------------------------------------------
    # START
    # --------------------------------------------------------

    graph.add_edge(
        START,
        "idea_generator",
    )

    graph.add_conditional_edges(
        "idea_generator",
        route_after_idea_generator,
        {"executive_producer": "executive_producer", "stop": END},
    )
    graph.add_conditional_edges(
        "executive_producer",
        route_after_executive_producer,
        {"critic": "idea_critic", "regenerate": "idea_generator", "stop": END},
    )
    graph.add_conditional_edges(
        "idea_critic",
        route_after_critic,
        {"develop": "concept_developer", "regenerate": "idea_generator", "stop": END},
    )
    graph.add_edge("concept_developer", "research_agent")
    graph.add_edge("research_agent", END)

    return graph.compile()
