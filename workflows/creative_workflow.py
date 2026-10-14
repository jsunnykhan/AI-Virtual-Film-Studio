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

import asyncio
from datetime import datetime, timezone
import json
import logging
from pathlib import Path
from typing import Any
import uuid

# ============================================================
# PERSISTENCE HELPER
# ============================================================


def save_creative_concept(state: dict[str, Any]) -> dict[str, Any]:
    """Persists creative workflow deliverables to output/creative_concepts.json."""
    output_dir = Path("output")
    output_dir.mkdir(parents=True, exist_ok=True)
    catalog_path = output_dir / "creative_concepts.json"

    concept_output = state.get("concept", {}).get("output", {})
    idea_output = state.get("idea", {}).get("output", {})
    critique_output = state.get("critique", {}).get("output", {})
    ep_output = state.get("final_decision", {}).get("output", {})
    research_output = state.get("research", {}).get("output", {})

    title = (
        concept_output.get("title")
        or idea_output.get("title")
        or ep_output.get("title")
        or "Untitled Concept"
    )

    record = {
        "project_id": state.get("project_id"),
        "title": title,
        "format": concept_output.get("format") or ep_output.get("format") or "series",
        "genre": concept_output.get("genre") or ep_output.get("genre") or [],
        "logline": concept_output.get("logline") or idea_output.get("premise") or "",
        "series_premise": concept_output.get("series_premise", ""),
        "core_theme": concept_output.get("core_theme", ""),
        "characters_count": len(concept_output.get("characters", [])),
        "critic_verdict": critique_output.get("verdict", "reviewed"),
        "executive_approved": ep_output.get("approved", True),
        "research_completed": bool(research_output),
        "status": state.get("status", "completed"),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    existing = []
    if catalog_path.exists():
        try:
            existing = json.loads(catalog_path.read_text(encoding="utf-8"))
        except Exception:
            existing = []
    existing.append(record)
    catalog_path.write_text(json.dumps(existing, indent=2), encoding="utf-8")
    return record


# ============================================================
# ROUTER
# ============================================================


def route_after_idea_generator(
    state: CreativeWorkflowState,
) -> str:
    idea = state.get("idea", {})
    return "executive_producer" if idea.get("success", False) else "stop"


def route_after_executive_producer(
    state: CreativeWorkflowState,
) -> str:
    decision = state.get("final_decision", {})
    if not decision.get("success", False):
        return "stop"

    output = decision.get("output") or {}
    if output.get("approved") is True or output.get("approved") is None:
        return "critic"

    if state.get("iteration", 0) < state.get("max_iterations", 3):
        return "regenerate"
    return "critic"


def route_after_critic(
    state: CreativeWorkflowState,
) -> str:
    critique = state.get("critique", {})
    if not critique.get("success", False):
        return "stop"

    output = critique.get("output") or {}
    verdict = output.get("verdict", "")
    if verdict in ("strong_candidate", "approved", "needs_revision", ""):
        return "develop"

    if state.get("iteration", 0) < state.get("max_iterations", 3):
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


if __name__ == "__main__":
    import sys

    prompt = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "Autonomously develop an original sci-fi or animated fantasy series concept."
    )

    async def main():
        wf = build_creative_workflow()
        project_id = f"creative_{uuid.uuid4().hex[:8]}"
        print(f"🎬 Triggering Creative Workflow for project: {project_id}")
        print(f"Prompt: {prompt}")
        result = await wf.ainvoke({
            "project_id": project_id,
            "user_request": prompt,
            "iteration": 0,
            "max_iterations": 3,
            "status": "started",
        })
        saved = save_creative_concept(result)
        print("\n✅ Creative Workflow Complete!")
        print(f"Title: {saved.get('title')}")
        print(f"Logline: {saved.get('logline')}")
        print(f"Critic Verdict: {saved.get('critic_verdict')}")
        print(f"Saved to: output/creative_concepts.json")

    asyncio.run(main())
