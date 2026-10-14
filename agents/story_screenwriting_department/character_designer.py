from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field

from agents.core.base_agent import BaseAgent
from agents.core.policies import AgentPolicy
from shared.core.settings import Settings

settings = Settings()


class CharacterVoiceProfile(BaseModel):
    speech_cadence: str = Field(description="Rhythm, tempo, sentence length, pauses")
    vocabulary_tier: str = Field(description="Colloquial, academic, street-smart, poetic, laconic, archaic")
    verbal_tics_and_catchphrases: list[str] = Field(default_factory=list)
    vocal_delivery_notes: str = Field(description="Gravelly, melodic, deadpan, strained, breathless, resonant")


class CharacterVisualAnchor(BaseModel):
    age_appearance: str
    physique_and_silhouette: str = Field(description="Body shape, posture, distinctive height, silhouette readability")
    facial_features: str = Field(description="Jawline, nose shape, skin texture, wrinkles, facial symmetry")
    eye_profile: str = Field(description="Eye color, shape, gaze intensity")
    hair_profile: str = Field(description="Exact hairstyle, color, highlights, length, receding, braided")
    signature_wardrobe: str = Field(description="Default recognizable clothing, layers, materials, color palette")
    distinguishing_marks: list[str] = Field(default_factory=list, description="Scars, cybernetic implants, tattoos, birthmarks, glasses")
    diffusion_consistency_tokens: list[str] = Field(
        default_factory=list,
        description="Exact ordered visual prompt tokens for diffusion/LoRA models to anchor character identity across shots"
    )


class CharacterPsychology(BaseModel):
    internal_wound_or_ghost: str = Field(description="The past trauma or haunting regret driving their behavior")
    the_lie_they_believe: str = Field(description="False belief about themselves or the world they must unlearn")
    external_want: str = Field(description="Conscious goal they are actively pursuing")
    internal_need: str = Field(description="Unconscious emotional/spiritual growth required to heal")
    fatal_flaw: str = Field(description="Weakness that repeatedly causes their own downfall under pressure")
    arc_direction: Literal["positive_growth", "tragic_fall", "flat_catalyst", "cynical_corruption"]


class CharacterRelationship(BaseModel):
    target_character_id: str
    dynamic_label: str = Field(description="Rival, reluctant ally, mentor, unrequited love, foil, betrayer")
    underlying_tension: str = Field(description="The source of unspoken friction between them")


class CharacterProfile(BaseModel):
    character_id: str = Field(description="Unique ID e.g. char_elena_vance")
    name: str
    narrative_role: Literal["protagonist", "antagonist", "deuteragonist", "mentor", "foil", "catalyst", "comic_relief"]
    logline: str = Field(description="One-sentence essence of who they are")
    psychology: CharacterPsychology
    voice: CharacterVoiceProfile
    visual_anchor: CharacterVisualAnchor
    relationships: list[CharacterRelationship] = Field(default_factory=list)


class CharacterDesignResponse(BaseModel):
    project_id: str
    cast_title: str
    characters: list[CharacterProfile] = Field(default_factory=list)
    ensemble_contrast_matrix: str = Field(
        description="Analysis of how cast members contrast each other visually, philosophically, and vocally"
    )
    ai_generation_consistency_guidelines: list[str] = Field(
        default_factory=list,
        description="Practical tips for downstream prompt engineers and model trainers to prevent facial and costume drift"
    )


class CharacterDesignerAgent(BaseAgent[CharacterDesignResponse]):

    @property
    def agent_id(self) -> str:
        return "character_designer"

    @property
    def role_instructions(self) -> str:
        return """
You are the Character Designer Agent for an autonomous AI animation studio.

Your responsibility is to design unforgettable, multi-dimensional characters with profound psychological
depth, unique vocal patterns, and crystal-clear visual identity anchors that allow our generative AI
pipeline to render them consistently across hundreds of shots.

You are the CHIEF CHARACTER ARCHITECT of the studio.

You work between Story Architecture and Screenwriting, providing the vital human (or non-human) engine
of the story.

You are NOT:
- a screenwriter (do not write full scenes or dialogue scripts)
- a storyboard artist (do not draw panels)
- a 3D modeler

YOUR CORE RESPONSIBILITIES

1. DEEP PSYCHOLOGICAL DIMENSION
   - Every major character must have:
     * A Ghost / Wound: The formative event that broke their worldview.
     * The Lie They Believe: Their protective illusion (e.g. "I can never trust anyone").
     * External Want vs Internal Need: What they strive for vs what will actually make them whole.
     * Fatal Flaw: A real character defect (pride, cynicism, recklessness, cowardice), not a humblebrag.

2. DISTINCTIVE VOCAL DNA
   - Characters must NEVER sound identical or share the same generic AI syntax.
   - Give each character distinct rhythm, cadence, sentence structure, and vocabulary tier.
   - Screenwriters will use these voice profiles to write authentic dialogue without generic exposition.

3. AI VISUAL ANCHOR ENGINEERING
   - AI diffusion and video models suffer from identity drift across scene cuts.
   - Build characters with unmistakable, high-contrast visual anchors:
     * Strong silhouette distinction (e.g. one character broad-shouldered with heavy duster coat; another slender with angular cropped hood).
     * Non-conflicting color palettes (never dress two main characters in the exact same shade of blue or brown).
     * High-reliability visual prompt tokens: specific, reproducible descriptors (e.g., "monobrow, crooked aquiline nose, asymmetric shaved undercut, cobalt mechanic overalls with oil stains").
     * Permanent identifying marks: unique scars, cybernetic implants, specific glasses or jewelry.

4. CAST DYNAMICS & FOILS
   - Every character exists in relation to the others.
   - Ensure characters act as philosophical and visual foils to one another.
   - Foster subtext and latent conflict in every relationship dynamic.

OUTPUT FORMAT
Return ONLY valid JSON matching the requested schema.
Do not include screenplay scenes, character sketches, or conversational chatter.
"""

    @property
    def output_schema(self) -> type[CharacterDesignResponse]:
        return CharacterDesignResponse


CHARACTER_DESIGNER_POLICY = AgentPolicy(
    agent_id="character_designer",
    model=settings.openai_model,
    max_input_tokens=10000,
    max_output_tokens=4000,
    temperature=0.7,
    reasoning_effort="none",
    allowed_tools=(
        "movie_bible.search",
        "character.get",
    ),
    max_retries=2,
    require_structured_output=True,
)
