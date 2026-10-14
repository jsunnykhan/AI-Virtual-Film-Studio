from __future__ import annotations

import logging
from pathlib import Path
from typing import Any
from uuid import uuid4

from agents.core.schemas import AgentTask
from agents.core.states import CreativeWorkflowState, MovieWorkflowState
from agents.agent_container import (
    idea_generator,
    idea_critic,
    concept_developer,
    executive_producer,
    production_manager,
    research_agent,
    story_architect,
    world_designer,
    character_designer,
    screenwriter,
    script_editor,
    director,
    cinematographer,
    storyboard_artist,
    shot_planner,
    production_designer,
    voice_director,
    music_sound_designer,
    prompt_engineer,
    generation_supervisor,
    editor,
    finishing_supervisor,
    continuity_qc,
    rights_delivery_reviewer,
)
from tools.comfyui import ComfyUIClient
from tools.video_assembler import VideoAssembler

logger = logging.getLogger(__name__)


# ============================================================
# CREATIVE & EXECUTIVE NODES
# ============================================================


async def idea_generator_node(state: MovieWorkflowState | CreativeWorkflowState):
    task = AgentTask(
        task_id=state.get("task_id") or str(uuid4()),
        project_id=state.get("project_id", ""),
        agent_id="idea_generator",
        objective=(
            "Autonomously generate an original animated series or movie concept. "
            "Choose the format, genre, and story suitable for AI video production."
        ),
        input_data={
            "user_request": state.get("user_request", "Original cinematic animated production"),
            "iteration": state.get("iteration", 0),
            "max_iterations": state.get("max_iterations", 3),
            "previous_idea": state.get("idea"),
            "executive_feedback": state.get("final_decision"),
            "critic_feedback": state.get("critique"),
        },
    )
    result = await idea_generator.run(task)
    return {
        "task_id": task.task_id,
        "iteration": state.get("iteration", 0) + 1,
        "idea": result.model_dump(),
        "status": "idea_generated" if result.success else "idea_generation_failed",
        "error": "; ".join(result.errors) if result.errors else None,
    }


async def executive_producer_node(state: MovieWorkflowState | CreativeWorkflowState):
    task = AgentTask(
        task_id=state.get("task_id") or str(uuid4()),
        project_id=state.get("project_id", ""),
        agent_id="executive_producer",
        objective="Review the creative concept and establish the production brief.",
        input_data={
            "user_request": state.get("user_request", ""),
            "idea": state.get("idea"),
            "critique": state.get("critique", {}),
            "concept": state.get("concept", {}),
        },
    )
    result = await executive_producer.run(task)
    return {
        "final_decision": result.model_dump(),
        "status": (
            "executive_approved"
            if result.success and result.output and getattr(result.output, "approved", True)
            else "executive_rejected" if result.success else "executive_producer_failed"
        ),
        "error": "; ".join(result.errors) if result.errors else None,
    }


async def idea_critic_node(state: MovieWorkflowState | CreativeWorkflowState):
    task = AgentTask(
        task_id=state.get("task_id") or str(uuid4()),
        project_id=state.get("project_id", ""),
        agent_id="idea_critic",
        objective="Critique the generated concept for originality, episode engine, and feasibility.",
        input_data={
            "user_request": state.get("user_request", ""),
            "idea": state.get("idea"),
            "iteration": state.get("iteration", 0),
        },
    )
    result = await idea_critic.run(task)
    return {
        "critique": result.model_dump(),
        "status": "idea_criticized" if result.success else "idea_critic_failed",
        "error": "; ".join(result.errors) if result.errors else None,
    }


async def concept_developer_node(state: MovieWorkflowState | CreativeWorkflowState):
    task = AgentTask(
        task_id=state.get("task_id") or str(uuid4()),
        project_id=state.get("project_id", ""),
        agent_id="concept_developer",
        objective="Develop the approved idea into a complete production series/movie concept blueprint.",
        input_data={
            "user_request": state.get("user_request", ""),
            "idea": state.get("idea"),
            "critique": state.get("critique", {}),
        },
    )
    result = await concept_developer.run(task)
    return {
        "concept": result.model_dump(),
        "status": "concept_developed" if result.success else "concept_development_failed",
        "error": "; ".join(result.errors) if result.errors else None,
    }


async def research_agent_node(state: MovieWorkflowState | CreativeWorkflowState):
    task = AgentTask(
        task_id=state.get("task_id") or str(uuid4()),
        project_id=state.get("project_id", ""),
        agent_id="research_agent",
        objective="Gather research findings to ground story world, science, and visual design.",
        input_data={
            "user_request": state.get("user_request", ""),
            "idea": state.get("idea"),
            "concept": state.get("concept", {}),
        },
    )
    result = await research_agent.run(task)
    return {
        "research": result.model_dump(),
        "status": "research_completed" if result.success else "research_failed",
        "error": "; ".join(result.errors) if result.errors else None,
    }


async def production_manager_node(state: MovieWorkflowState):
    ep_decision = state.get("final_decision", {}).get("output", {})
    concept_output = state.get("concept", {}).get("output", {})
    suggested_duration = ep_decision.get("duration") or concept_output.get("duration")

    task = AgentTask(
        task_id=state.get("task_id") or str(uuid4()),
        project_id=state.get("project_id", ""),
        agent_id="production_manager",
        objective=(
            "Autonomously determine the optimal project runtime duration in minutes (e.g. 5, 20, 90, 120, or up to 200+ minutes) "
            "based on narrative scope, format, and creative vision. Formulate the comprehensive production schedule and resource plan."
        ),
        input_data={
            "suggested_duration": suggested_duration,
            "brief": state.get("final_decision", {}),
            "concept": state.get("concept", {}),
        },
    )
    result = await production_manager.run(task)

    decided_runtime = None
    if result.success and result.output:
        decided_runtime = getattr(result.output, "target_runtime_minutes", None)

    return {
        "production_plan": result.model_dump(),
        "target_duration_minutes": decided_runtime or state.get("target_duration_minutes"),
        "status": "production_planned" if result.success else "production_plan_failed",
        "error": "; ".join(result.errors) if result.errors else None,
    }


# ============================================================
# STORY & SCREENWRITING NODES
# ============================================================


async def story_architect_node(state: MovieWorkflowState):
    target_minutes = state.get("target_duration_minutes")
    task = AgentTask(
        task_id=state.get("task_id") or str(uuid4()),
        project_id=state.get("project_id", ""),
        agent_id="story_architect",
        objective=f"Architect dramatic beats and scene outlines scaled to the project runtime ({target_minutes or 'AI-determined'} minutes).",
        input_data={
            "concept": state.get("concept", {}),
            "research": state.get("research", {}),
            "target_duration_minutes": target_minutes,
        },
    )
    result = await story_architect.run(task)
    return {
        "story_architecture": result.model_dump(),
        "status": "story_architected" if result.success else "story_architecture_failed",
        "error": "; ".join(result.errors) if result.errors else None,
    }


async def world_designer_node(state: MovieWorkflowState):
    task = AgentTask(
        task_id=state.get("task_id") or str(uuid4()),
        project_id=state.get("project_id", ""),
        agent_id="world_designer",
        objective="Design canonical locations, physical rules, and visual anchor tokens.",
        input_data={
            "concept": state.get("concept", {}),
            "story": state.get("story_architecture", {}),
        },
    )
    result = await world_designer.run(task)
    return {
        "world_design": result.model_dump(),
        "status": "world_designed" if result.success else "world_design_failed",
        "error": "; ".join(result.errors) if result.errors else None,
    }


async def character_designer_node(state: MovieWorkflowState):
    task = AgentTask(
        task_id=state.get("task_id") or str(uuid4()),
        project_id=state.get("project_id", ""),
        agent_id="character_designer",
        objective="Create multi-dimensional character profiles and AI visual consistency prompt anchors.",
        input_data={
            "concept": state.get("concept", {}),
            "story": state.get("story_architecture", {}),
        },
    )
    result = await character_designer.run(task)
    return {
        "character_design": result.model_dump(),
        "status": "characters_designed" if result.success else "character_design_failed",
        "error": "; ".join(result.errors) if result.errors else None,
    }


async def screenwriter_node(state: MovieWorkflowState):
    target_minutes = state.get("target_duration_minutes")
    duration_prompt = f"totaling approximately {target_minutes} minutes" if target_minutes else "with appropriate scenes for the planned story arc"
    task = AgentTask(
        task_id=state.get("task_id") or str(uuid4()),
        project_id=state.get("project_id", ""),
        agent_id="screenwriter",
        objective=f"Write complete screenplay scenes {duration_prompt}.",
        input_data={
            "story": state.get("story_architecture", {}),
            "characters": state.get("character_design", {}),
            "world": state.get("world_design", {}),
            "target_duration_minutes": target_minutes,
        },
    )
    result = await screenwriter.run(task)
    return {
        "screenplay": result.model_dump(),
        "status": "screenplay_written" if result.success else "screenplay_failed",
        "error": "; ".join(result.errors) if result.errors else None,
    }


async def script_editor_node(state: MovieWorkflowState):
    task = AgentTask(
        task_id=state.get("task_id") or str(uuid4()),
        project_id=state.get("project_id", ""),
        agent_id="script_editor",
        objective="Polish screenplay, remove exposition dumps, and tighten pacing.",
        input_data={
            "screenplay": state.get("screenplay", {}),
            "characters": state.get("character_design", {}),
        },
    )
    result = await script_editor.run(task)
    return {
        "script_edit": result.model_dump(),
        "status": "script_edited" if result.success else "script_edit_failed",
        "error": "; ".join(result.errors) if result.errors else None,
    }


# ============================================================
# DIRECTING & PRODUCTION DESIGN NODES
# ============================================================


async def director_node(state: MovieWorkflowState):
    task = AgentTask(
        task_id=state.get("task_id") or str(uuid4()),
        project_id=state.get("project_id", ""),
        agent_id="director",
        objective="Establish directorial treatment, blocking, pacing tempo, and emotional targets.",
        input_data={
            "screenplay": state.get("screenplay", {}),
            "script_edit": state.get("script_edit", {}),
            "world": state.get("world_design", {}),
            "characters": state.get("character_design", {}),
        },
    )
    result = await director.run(task)
    return {
        "directorial_vision": result.model_dump(),
        "status": "direction_set" if result.success else "director_failed",
        "error": "; ".join(result.errors) if result.errors else None,
    }


async def cinematographer_node(state: MovieWorkflowState):
    task = AgentTask(
        task_id=state.get("task_id") or str(uuid4()),
        project_id=state.get("project_id", ""),
        agent_id="cinematographer",
        objective="Specify camera lenses, lighting setups, color grading palettes, and optical rules.",
        input_data={
            "director": state.get("directorial_vision", {}),
            "screenplay": state.get("screenplay", {}),
        },
    )
    result = await cinematographer.run(task)
    return {
        "cinematography": result.model_dump(),
        "status": "cinematography_set" if result.success else "cinematographer_failed",
        "error": "; ".join(result.errors) if result.errors else None,
    }


async def production_designer_node(state: MovieWorkflowState):
    task = AgentTask(
        task_id=state.get("task_id") or str(uuid4()),
        project_id=state.get("project_id", ""),
        agent_id="production_designer",
        objective="Design physical sets, hero props, costume layers, and tactile material swatches.",
        input_data={
            "world": state.get("world_design", {}),
            "screenplay": state.get("screenplay", {}),
            "director": state.get("directorial_vision", {}),
        },
    )
    result = await production_designer.run(task)
    return {
        "production_design": result.model_dump(),
        "status": "production_design_set" if result.success else "production_designer_failed",
        "error": "; ".join(result.errors) if result.errors else None,
    }


async def storyboard_artist_node(state: MovieWorkflowState):
    task = AgentTask(
        task_id=state.get("task_id") or str(uuid4()),
        project_id=state.get("project_id", ""),
        agent_id="storyboard_artist",
        objective="Choreograph panel compositions, 180-degree axis, and visual eye-trace continuity.",
        input_data={
            "screenplay": state.get("screenplay", {}),
            "director": state.get("directorial_vision", {}),
            "cinematography": state.get("cinematography", {}),
        },
    )
    result = await storyboard_artist.run(task)
    return {
        "storyboard": result.model_dump(),
        "status": "storyboard_created" if result.success else "storyboard_artist_failed",
        "error": "; ".join(result.errors) if result.errors else None,
    }


async def shot_planner_node(state: MovieWorkflowState):
    target_minutes = state.get("target_duration_minutes")
    target_seconds = (target_minutes * 60.0) if target_minutes else None
    duration_prompt = f"totaling approximately {int(target_seconds)} seconds ({target_minutes} minutes)" if target_seconds else "matching the screenplay scene breakdown"

    task = AgentTask(
        task_id=state.get("task_id") or str(uuid4()),
        project_id=state.get("project_id", ""),
        agent_id="shot_planner",
        objective=f"Plan sequential shots at 24fps {duration_prompt}.",
        input_data={
            "screenplay": state.get("screenplay", {}),
            "cinematography": state.get("cinematography", {}),
            "storyboard": state.get("storyboard", {}),
            "target_duration_seconds": target_seconds,
        },
    )
    result = await shot_planner.run(task)
    return {
        "shot_plan": result.model_dump(),
        "status": "shots_planned" if result.success else "shot_planner_failed",
        "error": "; ".join(result.errors) if result.errors else None,
    }


# ============================================================
# AUDIO NODES
# ============================================================


async def voice_director_node(state: MovieWorkflowState):
    task = AgentTask(
        task_id=state.get("task_id") or str(uuid4()),
        project_id=state.get("project_id", ""),
        agent_id="voice_director",
        objective="Score voice performances, dialogue delivery, pacing, and breath markers.",
        input_data={
            "screenplay": state.get("screenplay", {}),
            "characters": state.get("character_design", {}),
            "director": state.get("directorial_vision", {}),
        },
    )
    result = await voice_director.run(task)
    return {
        "voice_direction": result.model_dump(),
        "status": "voice_directed" if result.success else "voice_director_failed",
        "error": "; ".join(result.errors) if result.errors else None,
    }


async def music_sound_designer_node(state: MovieWorkflowState):
    task = AgentTask(
        task_id=state.get("task_id") or str(uuid4()),
        project_id=state.get("project_id", ""),
        agent_id="music_sound_designer",
        objective="Design musical score cues, leitmotifs, Foley, and ambient beds for the scene.",
        input_data={
            "screenplay": state.get("screenplay", {}),
            "shot_plan": state.get("shot_plan", {}),
            "director": state.get("directorial_vision", {}),
        },
    )
    result = await music_sound_designer.run(task)
    return {
        "music_sound_design": result.model_dump(),
        "status": "audio_designed" if result.success else "music_sound_designer_failed",
        "error": "; ".join(result.errors) if result.errors else None,
    }


# ============================================================
# GENERATION & COMFYUI NODES
# ============================================================


async def prompt_engineer_node(state: MovieWorkflowState):
    task = AgentTask(
        task_id=state.get("task_id") or str(uuid4()),
        project_id=state.get("project_id", ""),
        agent_id="prompt_engineer",
        objective="Synthesize model-specific generative prompts and camera motion commands for ComfyUI.",
        input_data={
            "shot_plan": state.get("shot_plan", {}),
            "cinematography": state.get("cinematography", {}),
            "characters": state.get("character_design", {}),
            "production_design": state.get("production_design", {}),
        },
    )
    result = await prompt_engineer.run(task)
    return {
        "prompts": result.model_dump(),
        "status": "prompts_engineered" if result.success else "prompt_engineer_failed",
        "error": "; ".join(result.errors) if result.errors else None,
    }


async def generation_supervisor_node(state: MovieWorkflowState):
    task = AgentTask(
        task_id=state.get("task_id") or str(uuid4()),
        project_id=state.get("project_id", ""),
        agent_id="generation_supervisor",
        objective="Formulate multi-pass rendering batches and seed management strategy for ComfyUI execution.",
        input_data={
            "prompts": state.get("prompts", {}),
            "shot_plan": state.get("shot_plan", {}),
        },
    )
    result = await generation_supervisor.run(task)
    return {
        "render_supervision": result.model_dump(),
        "status": "generation_supervised" if result.success else "generation_supervisor_failed",
        "error": "; ".join(result.errors) if result.errors else None,
    }


# ============================================================
# COMFYUI RENDERING & VIDEO ASSEMBLY (Commented out: Pending ComfyUI URL)
# ============================================================

# async def comfyui_generation_node(state: MovieWorkflowState):
#     """
#     [COMMENTED OUT PENDING COMFYUI URL]
#     Renders video shots via ComfyUI API and downloads rendered video clips to local media directory.
#     """
#     project_id = state.get("project_id") or str(uuid4())
#     prompts_data = state.get("prompts", {}).get("output", {})
#     shot_prompts = prompts_data.get("prompts", [])
#     output_dir = Path("output") / "projects" / project_id / "shots"
#     output_dir.mkdir(parents=True, exist_ok=True)
#     client = ComfyUIClient()
#     rendered_shot_paths: list[str] = []
#     ...
#     return {"rendered_shot_paths": rendered_shot_paths, "status": "comfyui_renders_completed"}


# async def video_assembly_node(state: MovieWorkflowState):
#     """
#     [COMMENTED OUT PENDING COMFYUI URL]
#     Merges downloaded shot clips into a complete scene video with FFmpeg.
#     """
#     ...
#     return {"assembled_scene_path": "...", "status": "video_assembly_completed"}


# ============================================================
# POST-PRODUCTION NODES
# ============================================================


async def editor_node(state: MovieWorkflowState):
    target_minutes = state.get("target_duration_minutes")
    task = AgentTask(
        task_id=state.get("task_id") or str(uuid4()),
        project_id=state.get("project_id", ""),
        agent_id="editor",
        objective="Create master Edit Decision List (EDL) and cut sequence according to Murch's Rule of Six.",
        input_data={
            "shot_plan": state.get("shot_plan", {}),
            "prompts": state.get("prompts", {}),
            "target_duration_minutes": target_minutes,
        },
    )
    result = await editor.run(task)
    return {
        "editor_assembly": result.model_dump(),
        "status": "edit_assembled" if result.success else "editor_failed",
        "error": "; ".join(result.errors) if result.errors else None,
    }


async def finishing_supervisor_node(state: MovieWorkflowState):
    task = AgentTask(
        task_id=state.get("task_id") or str(uuid4()),
        project_id=state.get("project_id", ""),
        agent_id="finishing_supervisor",
        objective="Conform ACES color grade CDL, grain profile, and audio loudness mastering.",
        input_data={
            "assembled_scene_path": state.get("assembled_scene_path"),
            "cinematography": state.get("cinematography", {}),
            "editor_assembly": state.get("editor_assembly", {}),
        },
    )
    result = await finishing_supervisor.run(task)
    return {
        "finishing_conform": result.model_dump(),
        "status": "finishing_conformed" if result.success else "finishing_supervisor_failed",
        "error": "; ".join(result.errors) if result.errors else None,
    }


# ============================================================
# QUALITY & COMPLIANCE NODES
# ============================================================


async def continuity_qc_node(state: MovieWorkflowState):
    task = AgentTask(
        task_id=state.get("task_id") or str(uuid4()),
        project_id=state.get("project_id", ""),
        agent_id="continuity_qc",
        objective="Audit continuity across assembled shots, checking character facial identity and props.",
        input_data={
            "assembled_scene_path": state.get("assembled_scene_path"),
            "shot_plan": state.get("shot_plan", {}),
            "characters": state.get("character_design", {}),
        },
    )
    result = await continuity_qc.run(task)
    return {
        "continuity_report": result.model_dump(),
        "status": "continuity_audited" if result.success else "continuity_qc_failed",
        "error": "; ".join(result.errors) if result.errors else None,
    }


async def rights_delivery_node(state: MovieWorkflowState):
    task = AgentTask(
        task_id=state.get("task_id") or str(uuid4()),
        project_id=state.get("project_id", ""),
        agent_id="rights_delivery_reviewer",
        objective="Execute intellectual property clearance, safety ratings, and delivery release approval.",
        input_data={
            "final_movie_path": state.get("final_movie_path"),
            "concept": state.get("concept", {}),
            "research": state.get("research", {}),
        },
    )
    result = await rights_delivery_reviewer.run(task)
    return {
        "rights_clearance": result.model_dump(),
        "status": "production_completed" if result.success else "rights_delivery_failed",
        "error": "; ".join(result.errors) if result.errors else None,
    }