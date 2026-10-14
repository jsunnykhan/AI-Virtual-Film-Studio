from typing import Any, TypedDict


class CreativeWorkflowState(TypedDict, total=False):
    project_id: str
    workflow_id: str
    task_id: str
    user_request: str
    idea: dict[str, Any]
    ideas: list[dict[str, Any]]
    critique: dict[str, Any]
    final_decision: dict[str, Any]
    selected_idea: dict[str, Any] | None
    concept: dict[str, Any] | None
    research: dict[str, Any]
    iteration: int
    max_iterations: int
    status: str
    error: str | None


class MovieWorkflowState(TypedDict, total=False):
    project_id: str
    workflow_id: str
    task_id: str
    user_request: str
    format: str  # "movie", "series", "scene"
    target_duration_minutes: float  # e.g. 5.0 for a 5-minute scene
    iteration: int
    max_iterations: int

    # Creative & Executive
    idea: dict[str, Any]
    final_decision: dict[str, Any]
    critique: dict[str, Any]
    concept: dict[str, Any]
    research: dict[str, Any]
    production_plan: dict[str, Any]

    # Story & Screenwriting
    story_architecture: dict[str, Any]
    world_design: dict[str, Any]
    character_design: dict[str, Any]
    screenplay: dict[str, Any]
    script_edit: dict[str, Any]

    # Directing & Art
    directorial_vision: dict[str, Any]
    cinematography: dict[str, Any]
    production_design: dict[str, Any]
    storyboard: dict[str, Any]
    shot_plan: dict[str, Any]

    # Audio
    voice_direction: dict[str, Any]
    music_sound_design: dict[str, Any]

    # Generation & Rendering
    prompts: dict[str, Any]
    render_supervision: dict[str, Any]
    rendered_shot_paths: list[str]  # Individual downloaded shot video files from ComfyUI

    # Post-Production & Assembly
    editor_assembly: dict[str, Any]
    assembled_scene_path: str  # 5-minute merged scene video file
    assembled_scenes: list[str]  # List of merged scene videos
    final_movie_path: str  # Full merged movie/series video file
    finishing_conform: dict[str, Any]

    # Quality & Compliance
    continuity_report: dict[str, Any]
    rights_clearance: dict[str, Any]

    status: str
    error: str | None
