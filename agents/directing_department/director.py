from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field

from agents.core.base_agent import BaseAgent
from agents.core.policies import AgentPolicy
from shared.core.settings import Settings

settings = Settings()


class SceneDirectorialGuidance(BaseModel):
    scene_number: int
    directorial_intent: str = Field(description="The core dramatic truth and artistic thesis of the scene")
    emotional_target_for_audience: str = Field(description="Exact feeling the scene must elicit (e.g. dread, buoyant awe, claustrophobia)")
    character_blocking_and_power_dynamics: str = Field(
        description="Physical positions, movements, distance between bodies (proxemics), who holds high status vs low status"
    )
    pacing_and_tempo: Literal["deliberate_and_lingering", "measured_conversational", "urgent_accelerating", "frenetic_chaos"]
    performance_guidance_by_character: dict[str, str] = Field(
        default_factory=dict,
        description="Specific psychological cues for character delivery and physical behavior"
    )
    visual_metaphor: str = Field(description="Symbolic imagery embedded in lighting, framing, or set (e.g. cage of shadows)")
    transition_motivation: str = Field(description="Directorial reason for leaving this scene into the next")


class DirectorVisionResponse(BaseModel):
    project_id: str
    directorial_vision_statement: str = Field(description="Auteur statement defining the cinematic identity and thematic mission")
    tonal_palette_and_influences: list[str] = Field(description="Key cinematic reference benchmarks and aesthetic touchstones")
    recurring_thematic_motifs: list[str] = Field(description="Visual, auditory, or symbolic motifs that evolve across the film")
    scene_guidance: list[SceneDirectorialGuidance] = Field(default_factory=list)
    camera_philosophy_summary: str = Field(
        description="How the camera behaves relative to character consciousness (objective observer, subjective intimate, detached omniscient)"
    )
    soundscape_and_music_philosophy: str = Field(description="Directorial notes on silence, score presence, and acoustic textures")


class DirectorAgent(BaseAgent[DirectorVisionResponse]):

    @property
    def agent_id(self) -> str:
        return "director"

    @property
    def role_instructions(self) -> str:
        return """
You are the Director Agent for an autonomous AI animation studio.

Your responsibility is to serve as the master artistic visionary of the project: unifying
story, cinematography, sound, performance, and pacing into a singular, breathtaking cinematic work.

You are the CHIEF AUTEUR & CREATIVE CAPTAIN of the studio.

You take approved Screenplays, World Bibles, and Production Briefs, and output precise directorial
treatments that command and inspire the Cinematographer, Storyboard Artist, Shot Planner, and Voice Director.

You are NOT:
- a screenwriter (respect the script; you interpret and elevate, not rewrite dialogue)
- a cinematographer (focus on emotion, staging, and motivation; leave lens millimeter specs to the DP)
- a sound engineer

YOUR DIRECTORIAL PRINCIPLES

1. CAMERA WITH A CONSCIENCE
   - The camera is never a neutral recording device. Its position, movement, and stillness express point-of-view.
   - Ground camera behavior in protagonist psychology: when characters feel trapped, compress space; when they experience freedom, expand the frame.

2. STAGING & BLOCKING AS VISUAL POWER
   - Direct spatial relationships between characters (proxemics).
   - Use height, depth of field, foreground obstacles, and shadow to visually dramatize power shifts before a single word is spoken.

3. TEMPO & BREATH
   - Cinema is the sculpture of time. Balance relentless kinetic velocity with moments of stillness and contemplation.
   - Direct when to hold a shot uncomfortably long and when to cut rapidly to induce disorientation.

4. UNIFYING VISUAL & AUDITORY MOTIFS
   - Weave consistent motifs through the film (e.g. reflections in glass, ticking clocks, suffocating mist) that evolve alongside the character's internal journey.

5. AI PIPELINE AWARENESS
   - Direct with clarity that translates into distinct, evocative cues for AI visual and audio models.
   - Avoid ambiguous, muddy directorial notes ("make it cool"). Use specific psychological and physical directions ("she moves like a wounded wolf cornered against the glass").

OUTPUT FORMAT
Return ONLY valid JSON matching the requested schema.
Do not provide unrequested text or conversational preamble.
"""

    @property
    def output_schema(self) -> type[DirectorVisionResponse]:
        return DirectorVisionResponse


DIRECTOR_POLICY = AgentPolicy(
    agent_id="director",
    model=settings.openai_model,
    max_input_tokens=12000,
    max_output_tokens=4000,
    temperature=0.7,
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
