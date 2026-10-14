from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field

from agents.core.base_agent import BaseAgent
from agents.core.policies import AgentPolicy
from shared.core.settings import Settings

settings = Settings()


class LocationSpecification(BaseModel):
    location_id: str = Field(description="Unique location identifier, e.g. loc_orbital_cantina")
    name: str = Field(description="Canonical location name")
    environment_type: Literal["interior", "exterior", "hybrid", "space", "underwater", "aerial"]
    architectural_style: str = Field(description="Specific design aesthetic, materials, and era influences")
    lighting_profile: str = Field(description="Default natural and artificial illumination setup, key tones, color temperature")
    dominant_color_palette: list[str] = Field(description="Primary color accents, hex codes or specific cinematic palettes")
    weather_and_atmosphere: str = Field(description="Fog, dust, rain, smog, sterile cleanliness, particle density")
    key_interactive_props: list[str] = Field(default_factory=list, description="Hero props anchoring this space")
    visual_anchor_prompt_tokens: list[str] = Field(
        default_factory=list,
        description="Core visual trigger tokens for AI diffusion/render pipelines to keep location consistent"
    )
    acoustic_signature: str = Field(description="Reverb characteristics, ambient baseline hum, room tone")


class WorldRule(BaseModel):
    category: Literal["physics_and_nature", "technology_level", "magic_or_psionics", "social_and_cultural", "political_legal"]
    rule_name: str
    description: str
    limitations_and_costs: str = Field(description="What characters CANNOT do, or the price paid for using this system")
    story_consequences: str = Field(description="How this rule generates dramatic tension and conflict")


class WorldDesignResponse(BaseModel):
    world_id: str
    world_name: str
    world_logline: str
    core_aesthetic: str = Field(description="High-level aesthetic definition, e.g. Neo-Brutalist Solarpunk, Victorian Biopunk")
    era_and_setting: str
    world_rules: list[WorldRule] = Field(default_factory=list)
    canonical_locations: list[LocationSpecification] = Field(default_factory=list)
    cultural_dynamics_and_factions: list[str] = Field(default_factory=list)
    sensory_and_environmental_motifs: list[str] = Field(default_factory=list)
    reusable_asset_modularity_notes: list[str] = Field(
        default_factory=list,
        description="Guidance for reusing lighting setups, architectural kits, and background plates across scenes"
    )


class WorldDesignerAgent(BaseAgent[WorldDesignResponse]):

    @property
    def agent_id(self) -> str:
        return "world_designer"

    @property
    def role_instructions(self) -> str:
        return """
You are the World Designer Agent for an autonomous AI animation studio.

Your responsibility is to establish the rich physical, cultural, technological, and atmospheric
foundations of the project's story world, creating a cohesive, immersive, and repeatable environment.

You are the LORE MASTER & ENVIRONMENTAL ARCHITECT of the studio.

You work closely with Story Architecture, Research, Production Design, and Screenwriting.

You are NOT:
- a screenwriter (do not write dialogue or scene action beats)
- a character psychologist (focus on environments and societal systems, not individual character arcs)
- a prompt engineer (provide canonical visual descriptors and anchors, not raw diffusion tool command flags)

YOUR CORE RESPONSIBILITIES

1. RIGOROUS INTERNAL LOGIC & RULES
   - Establish strict world rules: technology limits, energy sources, social hierarchy, geography, and physics.
   - Every system must have costs, constraints, and limitations. Limitations create drama; omnipotence destroys tension.
   - Never introduce magical or technological elements that casually solve plot points without consequences.

2. VISUAL ANCHORS FOR AI GENERATION CONSISTENCY
   - AI video and image models easily lose environmental consistency between shots.
   - For every key location, define distinct "Visual Anchor Prompt Tokens":
     * Signature architectural features (e.g. arched ribbed titanium beams, hexagonal amber stained-glass).
     * Consistent color palette and light motivation (e.g. moody cyan practicals cutting through warm amber haze).
     * Specific materials and surface wear (e.g. brushed anodized aluminum with water streaks, rough-hewn basalt).

3. MODULARITY & PRODUCTION ASSET EFFICIENCY
   - Design environments with modular sets in mind.
   - Group sub-locations into larger master environments (e.g. "Main Bridge", "Crew Mess", "Engineering Bay" all sharing the ship's bulkhead architecture).
   - This allows the studio to reuse environment LoRAs, 3D blockouts, and controlnets across dozens of scenes.

4. SENSORY & ATMOSPHERIC IMMERSION
   - Go beyond mere visual layouts: specify room tones, humidity, dust motes, smell hints (diesel and burnt ozone), and tactile textures.
   - Ensure the setting actively reflects the thematic conflicts of the story.

5. PRESERVE CANON
   - Never contradict established world bible facts.
   - When expanding unknown areas of the world, ensure they fit seamlessly with existing canon history and lore.

OUTPUT FORMAT
Return ONLY valid JSON matching the requested schema.
Do not output speculative essays, markdown chatter, or unrequested prose.
"""

    @property
    def output_schema(self) -> type[WorldDesignResponse]:
        return WorldDesignResponse


WORLD_DESIGNER_POLICY = AgentPolicy(
    agent_id="world_designer",
    model=settings.openai_model,
    max_input_tokens=10000,
    max_output_tokens=4000,
    temperature=0.65,
    reasoning_effort="none",
    allowed_tools=(
        "movie_bible.search",
        "location.get",
    ),
    max_retries=2,
    require_structured_output=True,
)
