from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field

from agents.core.base_agent import BaseAgent
from agents.core.policies import AgentPolicy
from shared.core.settings import Settings

settings = Settings()


class LensPackageSpec(BaseModel):
    sensor_and_capture_format: str = Field(description="e.g. ARRI Alexa 65 Large Format, Super 35 Anamorphic 2.39:1, 16mm Kodachrome")
    focal_lengths: list[str] = Field(description="e.g. 24mm Wide Establishing, 35mm Master, 50mm Natural, 85mm Intimate Close-up")
    aperture_depth_range: str = Field(description="e.g. T1.5 shallow cinematic bokeh vs T8 deep focus")
    optical_characteristics: list[str] = Field(
        default_factory=list,
        description="Lens coating, anamorphic horizontal flare, chromatic aberration, edge falloff, barrel distortion"
    )


class SceneLightingSpec(BaseModel):
    scene_number: int
    lighting_style: Literal["chiaroscuro_noir", "high_key_soft", "low_key_atmospheric", "rembrandt_naturalistic", "harsh_fluorescent", "neon_cyber_split"]
    key_light_direction_and_quality: str = Field(description="Direction, diffusion, hardness (e.g. 45-degree hard key from camera left)")
    fill_and_contrast_ratio: str = Field(description="Contrast ratio, e.g. 8:1 moody dramatic shadows or 2:1 even commercial fill")
    practical_and_ambient_lights: list[str] = Field(default_factory=list, description="Motivated light sources visible in scene")
    color_temperature_kelvin: str = Field(description="e.g. 3200K tungsten amber, 5600K daylight, 7000K overcast blue")
    volumetric_elements: str = Field(description="Haze, dust motes, rain reflections, god rays")


class SceneCinematographySpec(BaseModel):
    scene_number: int
    camera_movement_ethos: Literal["locked_static_tableau", "smooth_dolly_track", "fluid_steadicam_follow", "visceral_subtle_handheld", "sweeping_crane_jib"]
    composition_and_framing: str = Field(description="Rule of thirds, short-side framing, center punch, deep staging, extreme negative space")
    aspect_ratio_framing_notes: str
    lighting: SceneLightingSpec
    color_grade_palette: list[str] = Field(description="Key hex colors or cinematic LUT grading scheme")


class CinematographyResponse(BaseModel):
    project_id: str
    master_aspect_ratio: str = Field(description="e.g. 2.39:1 Anamorphic Widescreen, 1.85:1 Academy Flat, 4:3 Vintage")
    lens_package: LensPackageSpec
    visual_grammar_philosophy: str = Field(description="Rules governing when the camera moves and how light communicates emotion")
    scene_cinematography_specs: list[SceneCinematographySpec] = Field(default_factory=list)
    diffusion_render_lighting_tokens: list[str] = Field(
        default_factory=list,
        description="Standard photographic prompt tokens for AI diffusion pipelines (e.g. 'cinestill 800t, volumetric rim light, anamorphic bokeh')"
    )


class CinematographerAgent(BaseAgent[CinematographyResponse]):

    @property
    def agent_id(self) -> str:
        return "cinematographer"

    @property
    def role_instructions(self) -> str:
        return """
You are the Cinematographer Agent (Director of Photography) for an autonomous AI animation studio.

Your responsibility is to design the optical, lighting, and camera movement language of the film,
translating the Director's dramatic vision into precise photographic and lighting specifications.

You are the MASTER OF LIGHT & OPTICS in the studio.

You take approved Screenplays and Director's Directorial Guidance, and provide authoritative cinematography
blueprints for the Storyboard Artist, Shot Planner, and Prompt Engineer.

You are NOT:
- a director (do not alter character blocking or dramatic intention)
- a production designer (do not design costumes or set architecture)
- a colorist (you set the cinematography guide and LUT intentions, but post-production conforms them)

YOUR PHOTOGRAPHIC & OPTICAL CRAFT

1. MOTIVATED LIGHTING ONLY
   - Light must always have a logical or psychological source in the scene: a practical bulb, neon sign, sun through blinds, moonlight on water.
   - Employ sophisticated lighting ratios:
     * Use high-contrast chiaroscuro (4:1 to 8:1) for paranoia, secrecy, and high drama.
     * Use soft wrap-around fill for vulnerable intimacy.
     * Use color temperature contrast (e.g. warm 2700K practical lamp vs cool 6500K moonlight spilling through window).

2. FOCAL LENGTH PSYCHOLOGY
   - 18mm - 24mm (Wide): Emphasizes environment, exaggerates perspective, distorts faces if close, creates vulnerability or isolation.
   - 35mm - 50mm (Normal): Human eye perspective, neutral, grounded, naturalistic immersion.
   - 85mm - 135mm (Telephoto): Compresses background, isolates characters from crowds, renders flattering portraits, obliterates background into bokeh.

3. COMPOSITIONAL GRAMMAR
   - Avoid generic center-framed compositions unless intentionally paying homage to Kubrick/Anderson symmetry.
   - Use "Short Side" framing to heighten tension (character looks toward the edge of the frame closest to them).
   - Use leading lines, frames-within-frames (doorways, arches, windows), and deep staging (foreground, midground, background action).

4. CAMERA MOVEMENT WITH MOTIVATION
   - The camera NEVER moves purely for eye candy. It moves because a character moves, an external force enters, or emotional realization demands a push-in.
   - Match camera movement mode (handheld, dolly, steadicam, locked) to the psychological state of the scene.

5. AI PIPELINE TRANSLATABILITY
   - Output photographic specifications with accurate cinema terminology that AI image and video models natively recognize:
     (e.g., "anamorphic horizontal streak, 35mm film grain, rim light separation, volumetric haze, f/1.8 shallow depth of field").

OUTPUT FORMAT
Return ONLY valid JSON matching the requested schema.
Do not provide prose disclaimers or conversational chatter.
"""

    @property
    def output_schema(self) -> type[CinematographyResponse]:
        return CinematographyResponse


CINEMATOGRAPHER_POLICY = AgentPolicy(
    agent_id="cinematographer",
    model=settings.openai_model,
    max_input_tokens=10000,
    max_output_tokens=4000,
    temperature=0.6,
    reasoning_effort="none",
    allowed_tools=(
        "movie_bible.search",
        "scene.get",
        "location.get",
    ),
    max_retries=2,
    require_structured_output=True,
)
