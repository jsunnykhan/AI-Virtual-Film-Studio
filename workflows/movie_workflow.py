from __future__ import annotations

import logging
from langgraph.graph import END, START, StateGraph

from agents.core.states import MovieWorkflowState
from workflows.nodes import (
    idea_generator_node,
    executive_producer_node,
    idea_critic_node,
    concept_developer_node,
    research_agent_node,
    production_manager_node,
    story_architect_node,
    world_designer_node,
    character_designer_node,
    screenwriter_node,
    script_editor_node,
    director_node,
    cinematographer_node,
    production_designer_node,
    storyboard_artist_node,
    shot_planner_node,
    voice_director_node,
    music_sound_designer_node,
    prompt_engineer_node,
    generation_supervisor_node,
    # comfyui_generation_node,  # Commented out: pending ComfyUI URL
    editor_node,
    # video_assembly_node,       # Commented out: pending ComfyUI renders
    finishing_supervisor_node,
    continuity_qc_node,
    rights_delivery_node,
)

logger = logging.getLogger(__name__)


# ============================================================
# CONDITIONAL ROUTING FUNCTIONS
# ============================================================


def route_after_idea_generator(state: MovieWorkflowState) -> str:
    idea = state.get("idea", {})
    return "executive_producer" if idea.get("success", False) else "stop"


def route_after_executive_producer(state: MovieWorkflowState) -> str:
    decision = state.get("final_decision", {})
    if not decision.get("success", False):
        return "stop"

    output = decision.get("output") or {}
    if output.get("approved") is True or output.get("approved") is None:
        return "critic"

    if state.get("iteration", 0) < state.get("max_iterations", 3):
        return "regenerate"
    return "critic"


def route_after_critic(state: MovieWorkflowState) -> str:
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
# WORKFLOW GRAPH BUILDER
# ============================================================


def build_movie_workflow():
    """
    Builds the end-to-end AI Movie & Series Production Workflow:
    1. Creative Development (Idea -> EP -> Critic -> Concept -> Research)
    2. Story & Script (Production Manager -> Story Architect -> World -> Character -> Screenplay -> Script Editor)
    3. Directing & Art (Director -> Cinematographer -> Production Designer -> Storyboard -> Shot Planner)
    4. Audio (Voice Director -> Music & Sound Designer)
    5. Generation (Prompt Engineer -> Generation Supervisor)
       [ComfyUI Render & Video Assembly commented out pending ComfyUI URL]
    6. Post-Production (Editor -> Finishing Supervisor)
    7. Quality & Release (Continuity QC -> Rights Delivery Reviewer -> Master Release)
    """
    graph = StateGraph(MovieWorkflowState)

    # 1. Register department nodes
    graph.add_node("idea_generator", idea_generator_node)
    graph.add_node("executive_producer", executive_producer_node)
    graph.add_node("idea_critic", idea_critic_node)
    graph.add_node("concept_developer", concept_developer_node)
    graph.add_node("research_agent", research_agent_node)

    graph.add_node("production_manager", production_manager_node)
    graph.add_node("story_architect", story_architect_node)
    graph.add_node("world_designer", world_designer_node)
    graph.add_node("character_designer", character_designer_node)
    graph.add_node("screenwriter", screenwriter_node)
    graph.add_node("script_editor", script_editor_node)

    graph.add_node("director", director_node)
    graph.add_node("cinematographer", cinematographer_node)
    graph.add_node("production_designer", production_designer_node)
    graph.add_node("storyboard_artist", storyboard_artist_node)
    graph.add_node("shot_planner", shot_planner_node)

    graph.add_node("voice_director", voice_director_node)
    graph.add_node("music_sound_designer", music_sound_designer_node)

    graph.add_node("prompt_engineer", prompt_engineer_node)
    graph.add_node("generation_supervisor", generation_supervisor_node)

    # --- ComfyUI & Video Assembly (commented out: pending ComfyUI URL) ---
    # graph.add_node("comfyui_generation", comfyui_generation_node)
    # graph.add_node("video_assembly", video_assembly_node)

    graph.add_node("editor", editor_node)
    graph.add_node("finishing_supervisor", finishing_supervisor_node)

    graph.add_node("continuity_qc", continuity_qc_node)
    graph.add_node("rights_delivery", rights_delivery_node)

    # 2. Add edges & conditional routing
    graph.add_edge(START, "idea_generator")

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

    # Linear pipeline progression through specialized departments
    graph.add_edge("concept_developer", "research_agent")
    graph.add_edge("research_agent", "production_manager")
    graph.add_edge("production_manager", "story_architect")
    graph.add_edge("story_architect", "world_designer")
    graph.add_edge("world_designer", "character_designer")
    graph.add_edge("character_designer", "screenwriter")
    graph.add_edge("screenwriter", "script_editor")

    graph.add_edge("script_editor", "director")
    graph.add_edge("director", "cinematographer")
    graph.add_edge("cinematographer", "production_designer")
    graph.add_edge("production_designer", "storyboard_artist")
    graph.add_edge("storyboard_artist", "shot_planner")

    graph.add_edge("shot_planner", "voice_director")
    graph.add_edge("voice_director", "music_sound_designer")

    graph.add_edge("music_sound_designer", "prompt_engineer")
    graph.add_edge("prompt_engineer", "generation_supervisor")

    # Connect generation supervisor directly to editor (bypassing ComfyUI render for now)
    # graph.add_edge("generation_supervisor", "comfyui_generation")
    # graph.add_edge("comfyui_generation", "editor")
    graph.add_edge("generation_supervisor", "editor")

    # Connect editor directly to finishing supervisor (bypassing video assembly for now)
    # graph.add_edge("editor", "video_assembly")
    # graph.add_edge("video_assembly", "finishing_supervisor")
    graph.add_edge("editor", "finishing_supervisor")

    graph.add_edge("finishing_supervisor", "continuity_qc")
    graph.add_edge("continuity_qc", "rights_delivery")
    graph.add_edge("rights_delivery", END)

    return graph.compile()


def build_scene_production_workflow():
    """
    Lightweight scene production workflow.
    (ComfyUI rendering tasks commented out pending ComfyUI URL).
    """
    graph = StateGraph(MovieWorkflowState)

    graph.add_node("shot_planner", shot_planner_node)
    graph.add_node("prompt_engineer", prompt_engineer_node)
    graph.add_node("generation_supervisor", generation_supervisor_node)
    # graph.add_node("comfyui_generation", comfyui_generation_node)
    graph.add_node("editor", editor_node)
    # graph.add_node("video_assembly", video_assembly_node)
    graph.add_node("finishing_supervisor", finishing_supervisor_node)

    graph.add_edge(START, "shot_planner")
    graph.add_edge("shot_planner", "prompt_engineer")
    graph.add_edge("prompt_engineer", "generation_supervisor")
    # graph.add_edge("generation_supervisor", "comfyui_generation")
    # graph.add_edge("comfyui_generation", "editor")
    graph.add_edge("generation_supervisor", "editor")
    # graph.add_edge("editor", "video_assembly")
    # graph.add_edge("video_assembly", "finishing_supervisor")
    graph.add_edge("editor", "finishing_supervisor")
    graph.add_edge("finishing_supervisor", END)

    return graph.compile()
