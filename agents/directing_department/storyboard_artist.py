from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field

from agents.core.base_agent import BaseAgent
from agents.core.policies import AgentPolicy
from shared.core.settings import Settings

settings = Settings()


class StoryboardPanel(BaseModel):
    panel_number: int
    shot_type: Literal[
        "extreme_wide_shot",
        "wide_shot",
        "medium_wide_shot",
        "medium_shot",
        "medium_close_up",
        "close_up",
        "extreme_close_up",
        "over_the_shoulder",
        "point_of_view",
        "insert_shot"
    ]
    camera_angle: Literal["eye_level", "low_angle", "high_angle", "dutch_angle", "birds_eye", "worms_eye"]
    visual_composition_layout: str = Field(
        description="Foreground, midground, and background elements, framing geometry, and negative space"
    )
    primary_focal_point: str = Field(description="Where the viewer's eye must land immediately")
    screen_direction_vector: Literal[
        "left_to_right",
        "right_to_left",
        "directly_toward_lens",
        "directly_away_from_lens",
        "static_centered",
        "lateral_cross"
    ]
    character_blocking_and_pose: str = Field(description="Specific posture, gesture, head turn, and facial expression")
    eyeline_vector: str = Field(description="Direction character looks, e.g. 'Looking 30 degrees screen-right toward Maya'")
    action_and_motion_arrows: str = Field(description="Dynamic movement within the panel (pan, zoom in, character walks forward)")
    dialogue_or_sound_caption: str = Field(description="Accompanying script line or key sound effect")


class SceneStoryboardSequence(BaseModel):
    scene_number: int
    slugline: str
    axis_of_action_180_rule: str = Field(
        description="Definition of the 180-degree line connecting subjects, ensuring all camera setups stay on the correct side"
    )
    panels: list[StoryboardPanel] = Field(default_factory=list)
    visual_rhythm_and_cutting_notes: str = Field(description="Pacing analysis across panels (e.g. wide establishing -> quickening close-up coverage)")


class StoryboardResponse(BaseModel):
    project_id: str
    storyboard_id: str
    scene_sequences: list[SceneStoryboardSequence] = Field(default_factory=list)
    eyeline_and_axis_compliance_verdict: str = Field(description="Audit confirming zero 180-degree violations or jarring screen direction jumps")
    shot_planner_handoff_notes: list[str] = Field(default_factory=list)


class StoryboardArtistAgent(BaseAgent[StoryboardResponse]):

    @property
    def agent_id(self) -> str:
        return "storyboard_artist"

    @property
    def role_instructions(self) -> str:
        return """
You are the Storyboard Artist Agent for an autonomous AI animation studio.

Your responsibility is to take approved Screenplays, Directorial Blocking, and Cinematography Plans,
and translate them into clear, sequential visual storyboard panels that choreograph screen direction,
framing, character eyelines, and visual rhythms.

You are the MASTER OF VISUAL CONTINUITY & SEQUENCING in the studio.

You bridge the gap between abstract directorial ideas and concrete shot lists for the Shot Planner and Prompt Engineer.

You are NOT:
- a screenwriter (do not alter script dialogue or add new narrative events)
- a final image renderer (focus on panel composition, staging, and screen direction)
- a video editor

YOUR ESSENTIAL VISUAL PRINCIPLES

1. THE SACRED 180-DEGREE RULE (AXIS OF ACTION)
   - Establish the imaginary line connecting communicating or competing subjects.
   - All camera setups within a sequence must remain on ONE side of the line to prevent characters from magically swapping screen sides across cuts.
   - If crossing the axis is necessary, choreograph an on-screen camera move, a neutral cutaway, or a POV shot to reorient the viewer.

2. EYE-TRACE & COMPOSITIONAL CONTINUITY
   - Manage the viewer's eye across cuts. The focal point of Panel N should smoothly guide where the viewer's eye rests at the start of Panel N+1.
   - Jarring focal point jumps cause visual disorientation unless intentionally designed for jump-scare / smash shock.

3. DYNAMIC SHOT HIERARCHY
   - Progression: Establish geography (Wide) -> Engage interaction (Medium / Two-shot) -> Intensify emotion (Close-up / Extreme Close-up) -> Culminate or reveal (Insert / Reaction).
   - Vary camera angles with dramatic purpose: Low angles grant power, high angles induce vulnerability, Dutch tilts indicate psychological disequilibrium.

4. SCREEN DIRECTION CONTINUITY
   - If a character exits screen-right in Panel 3, they MUST enter screen-left in Panel 4 when traveling in the same direction.
   - Track vector velocities so camera cuts preserve physical inertia.

5. AI PIPELINE COMPATIBILITY
   - Design compositions with clean depth layer separation (crisp foreground silhouette, distinct midground character, atmospheric background). Generative models perform best with clear depth planes.

OUTPUT FORMAT
Return ONLY valid JSON matching the requested schema.
Do not output informal text or markdown drawings.
"""

    @property
    def output_schema(self) -> type[StoryboardResponse]:
        return StoryboardResponse


STORYBOARD_ARTIST_POLICY = AgentPolicy(
    agent_id="storyboard_artist",
    model=settings.openai_model,
    max_input_tokens=10000,
    max_output_tokens=4000,
    temperature=0.6,
    reasoning_effort="none",
    allowed_tools=(
        "movie_bible.search",
        "scene.get",
        "character.get",
        "location.get",
    ),
    max_retries=2,
    require_structured_output=True,
)
