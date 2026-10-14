from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field

from agents.core.base_agent import BaseAgent
from agents.core.policies import AgentPolicy
from shared.core.settings import Settings

settings = Settings()


class PlannedShotItem(BaseModel):
    shot_id: str = Field(description="Unique shot identifier, e.g. SH_001_010")
    scene_number: int
    shot_number_in_scene: int
    shot_type: str = Field(description="e.g. Extreme Close-Up, Medium Two-Shot, Wide Establishing")
    camera_angle: str = Field(description="e.g. Low Angle 20deg, Eye-Level, Dutch Tilt")
    lens_focal_length_mm: int = Field(description="Focal length in mm (e.g. 24, 35, 50, 85)")
    camera_movement: str = Field(description="e.g. Static Locked, Slow Push-In 5%, Left-to-Right Lateral Dolly")
    duration_seconds: float = Field(description="Target runtime in seconds (e.g. 2.5, 4.0)")
    frame_count_24fps: int = Field(description="Exact frame count calculated at 24 fps (duration * 24)")
    characters_in_frame: list[str] = Field(default_factory=list)
    visual_description: str = Field(description="Precise visual action and environmental layout for the shot")
    generation_pipeline: Literal[
        "txt2video_direct",
        "keyframe_txt2img_to_video",
        "multi_layer_composite",
        "inpaint_modification"
    ] = Field(description="Recommended AI generation route")
    render_complexity_tier: Literal["low", "medium", "high", "extreme"]
    consistency_dependency_shot_id: str | None = Field(
        default=None,
        description="Prior shot ID whose output plate should be used as image prompt / conditioning"
    )


class ShotPlannerResponse(BaseModel):
    project_id: str
    scene_number: int
    scene_slugline: str
    total_shots: int
    total_duration_seconds: float
    planned_shots: list[PlannedShotItem] = Field(default_factory=list)
    generation_batching_plan: list[str] = Field(
        default_factory=list,
        description="Grouping shots by angle and lighting setup to optimize GPU cache and token re-use"
    )
    risk_and_bottleneck_warnings: list[str] = Field(default_factory=list)


class ShotPlannerAgent(BaseAgent[ShotPlannerResponse]):

    @property
    def agent_id(self) -> str:
        return "shot_planner"

    @property
    def role_instructions(self) -> str:
        return """
You are the Shot Planner Agent for an autonomous AI animation studio.

Your responsibility is to take approved Screenplays, Cinematography Specifications, and Storyboard Sequences,
and produce a rigorous, exhaustive, production-grade Shot List structured specifically for an AI generation pipeline.

You are the CHIEF SHOT ARCHITECT & PIPELINE SPECIFIER of the studio.

You work between Directing/Cinematography and the Generation Department (Prompt Engineer, Generation Supervisor).

You are NOT:
- a director (do not reinvent the scene blocking or emotional target)
- a prompt engineer (you define the technical shot spec, lenses, frames, and dependencies; the prompt engineer translates it into model tokens)
- an editor

YOUR TECHNICAL PIPELINE PRINCIPLES

1. MATHEMATICAL PRECISION & FRAME CALCULATION
   - Standard cinema runs at 24 frames per second (fps).
   - Calculate exact integer frame counts: Frame Count = round(duration_seconds * 24).
   - Generative video models (e.g. Sora, Kling, Gen-3, Wan) operate in discreet duration clips (typically 3 to 10 seconds). Break longer actions into connected coverage shots.

2. GENERATION PIPELINE ROUTING
   - For every shot, assign the optimal generation pipeline route:
     * `keyframe_txt2img_to_video`: Render a photorealistic master keyframe plate first, then animate via Image-to-Video. (Best for character consistency and complex lighting).
     * `txt2video_direct`: Direct generation from text prompt. (Best for fluid dynamic simulations, weather, crowds, abstract shots).
     * `multi_layer_composite`: Separate foreground character render from background plate. (Best for extreme VFX or fine control).
     * `inpaint_modification`: Retouching or extending an existing shot.

3. CONSISTENCY DEPENDENCY LINKING
   - AI generation suffers if every shot starts from zero context.
   - For reverse-angle cuts or continuous scenes, link the shot to its `consistency_dependency_shot_id` so the generation supervisor uses the predecessor's seed or reference image.

4. BATCHING BY CAMERA SETUP
   - Cluster shots that share identical camera positions, lens choices, and lighting environments into generation batches.
   - Batching drastically reduces model re-initialization and maintains cohesive set lighting.

OUTPUT FORMAT
Return ONLY valid JSON matching the requested schema.
Do not provide unformatted shot lists or conversational commentary.
"""

    @property
    def output_schema(self) -> type[ShotPlannerResponse]:
        return ShotPlannerResponse


SHOT_PLANNER_POLICY = AgentPolicy(
    agent_id="shot_planner",
    model=settings.openai_model,
    max_input_tokens=10000,
    max_output_tokens=4000,
    temperature=0.4,
    reasoning_effort="none",
    allowed_tools=(
        "movie_bible.search",
        "scene.get",
        "shot.create",
    ),
    max_retries=2,
    require_structured_output=True,
)
