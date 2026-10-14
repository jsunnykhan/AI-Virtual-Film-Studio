from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field

from agents.core.base_agent import BaseAgent
from agents.core.policies import AgentPolicy
from shared.core.settings import Settings

settings = Settings()


class SetDressingSpec(BaseModel):
    set_id: str = Field(description="Unique set ID, e.g. set_cantina_back_room")
    name: str
    architectural_style_and_materials: str = Field(
        description="e.g. Exposed reinforced concrete, oxidized steel beams, corrugated polycarbonate panels"
    )
    floor_and_ceiling_surfaces: str = Field(description="Scuffed linoleum, wet asphalt with oil sheen, exposed HVAC conduit")
    furnishings_and_set_dressing: list[str] = Field(
        default_factory=list,
        description="Specific tables, terminals, seating, shelving, cables, and lighting fixtures"
    )
    clutter_and_lived_in_density: Literal["sterile_minimalist", "orderly_functional", "lived_in_clutter", "chaotic_decay"]
    weathering_and_patina: str = Field(description="Salt corrosion, coffee stains, peeling wallpaper, dust blankets")


class HeroPropSpec(BaseModel):
    prop_id: str = Field(description="Unique prop ID, e.g. prop_emp_detonator")
    name: str
    associated_characters: list[str] = Field(default_factory=list)
    material_composition_and_finish: str = Field(description="e.g. Milled aircraft-grade aluminum, brass knurled dials, cracked OLED screen")
    wear_and_tear_narrative: str = Field(description="Visible history: scratches on grip, scorch marks, finger grease")
    interaction_mechanics: str = Field(description="How characters grip, flip, unlock, or activate it")
    prompt_anchor_tokens: list[str] = Field(
        default_factory=list,
        description="Specific visual prompt tokens for consistent rendering across scenes"
    )


class CostumeDesignSpec(BaseModel):
    character_id: str
    outfit_id: str
    outfit_context: str = Field(description="e.g. Battle Gear, Formal Gala, Civilian Disguise, Daily Utility")
    garment_layers: list[str] = Field(
        description="Base layer, middle layer, outerwear (e.g. ribbed merino wool turtleneck beneath oiled shearling aviator jacket)"
    )
    fabrics_and_textures: list[str] = Field(description="Specific textile weaves: heavy canvas, ripstop nylon, crushed velvet")
    palette_hex_codes: list[str] = Field(description="Color palette accents")
    distress_level: Literal["mint_pristine", "light_wear", "battle_damaged", "threadbare_decay"]
    silhouette_readability: str = Field(description="Distinctive visual profile in wide shots and shadows")


class ProductionDesignResponse(BaseModel):
    project_id: str
    production_design_bible_title: str
    aesthetic_credo: str = Field(description="Guiding philosophy of the visual world: materials, heritage, cultural design language")
    sets: list[SetDressingSpec] = Field(default_factory=list)
    hero_props: list[HeroPropSpec] = Field(default_factory=list)
    costumes: list[CostumeDesignSpec] = Field(default_factory=list)
    color_and_material_swatch_rules: list[str] = Field(default_factory=list)
    ai_diffusion_material_tokens: list[str] = Field(
        default_factory=list,
        description="Photorealistic texture tokens for diffusion pipelines to eliminate plastic/flat AI surfaces"
    )


class ProductionDesignerAgent(BaseAgent[ProductionDesignResponse]):

    @property
    def agent_id(self) -> str:
        return "production_designer"

    @property
    def role_instructions(self) -> str:
        return """
You are the Production Designer Agent for an autonomous AI animation studio.

Your responsibility is to design the tangible physical reality of the film: the architecture,
set dressing, hero props, costumes, textiles, wear-and-tear, and tactile material culture that give
the world visceral authenticity and historical weight.

You are the CHIEF VISUAL WORLD ARCHITECT & ART DIRECTOR of the studio.

You take approved Screenplays, World Bibles, and Director's Vision treatments, and supply authoritative
art department specifications to the Cinematographer, Shot Planner, and Prompt Engineer.

You are NOT:
- a screenwriter (do not alter script plot)
- a cinematographer (focus on physical objects, surfaces, and colors; leave lighting ratios to the DP)
- a 3D modeler

YOUR PRODUCTION DESIGN PRINCIPLES

1. TACTILE MATERIALITY & HISTORICAL LAYER
   - Worlds are rarely built all at once. Mix old and new: high-tech equipment wired into decaying 19th-century brickwork, or futuristic spacecraft with duct-taped wiring harnesses.
   - Specify real, sensory materials: milled brass, cast iron, oiled leather, ballistic nylon, oxidized copper, rough-hewn cedar.

2. BANISH THE "AI PLASTIC LOOK"
   - Generative models default to glossy, sterile, hyper-smooth plastic if left unguided.
   - Defeat this by demanding specific weathering: micro-scratches, dust motes in seams, greasy fingerprints on touchscreens, salt-water corrosion, chipped lacquer, fraying seams.

3. PROPS AS EXTENSIONS OF CHARACTER PSYCHOLOGY
   - Every hero prop tells a story before it is even used. A character's weapon, tool, or heirloom should reflect their psychological wound and history.

4. COSTUME SILHOUETTES & TEXTILE LAYERING
   - Costumes must be instantly recognizable in silhouette.
   - Design multi-layered outfits (undershirts, armor plates, scarves, holsters, boots) with contrasting textures (rough wool against smooth polished leather) to create rich visual depth.

5. ASSET REUSABILITY FOR AI PIPELINES
   - Organize set dressing and prop kits into modular families (e.g. "Standard Industrial Bulkhead Kit", "Outlaw Trading Post Props") that can be reused across multiple scenes, saving precious training and rendering budgets.

OUTPUT FORMAT
Return ONLY valid JSON matching the requested schema.
Do not provide narrative stories, drawing attachments, or conversational filler.
"""

    @property
    def output_schema(self) -> type[ProductionDesignResponse]:
        return ProductionDesignResponse


PRODUCTION_DESIGNER_POLICY = AgentPolicy(
    agent_id="production_designer",
    model=settings.openai_model,
    max_input_tokens=10000,
    max_output_tokens=4000,
    temperature=0.65,
    reasoning_effort="none",
    allowed_tools=(
        "movie_bible.search",
        "location.get",
        "character.get",
    ),
    max_retries=2,
    require_structured_output=True,
)
