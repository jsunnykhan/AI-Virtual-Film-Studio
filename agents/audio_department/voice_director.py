from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field

from agents.core.base_agent import BaseAgent
from agents.core.policies import AgentPolicy
from shared.core.settings import Settings

settings = Settings()


class CharacterVoiceSpec(BaseModel):
    character_id: str
    vocal_archetype_label: str = Field(description="e.g. Gritty Veteran, Calculating Prodigy, Warm Mentor")
    timbre_and_texture: str = Field(description="e.g. Raspy baritone with gravelly lower registers, luminous crisp soprano")
    vocal_pitch_and_register: Literal["bass", "baritone", "tenor", "contralto", "mezzo_soprano", "soprano", "child_neutral"]
    accent_dialect_and_idiosyncrasies: str = Field(
        description="e.g. Mid-Atlantic clipped vowels, mild Welsh cadence, synthesized vocoder harmonic"
    )
    tts_model_voice_id_or_embedding_anchor: str = Field(
        description="Reference model identifier or acoustic fingerprint descriptor"
    )


class LinePerformanceDirection(BaseModel):
    line_id: str
    scene_number: int
    character_name: str
    dialogue_text: str
    dramatic_objective: str = Field(description="What the character is trying to do to the listener with their voice")
    primary_emotional_charge: str = Field(description="e.g. Suppressed grief, icy fury, desperate plea, mock casualness")
    intensity_scale: int = Field(ge=1, le=10, description="1 is barely whispered mutter; 10 is explosive primal scream")
    speech_tempo: Literal["slow_deliberate_drawl", "measured_natural", "rapid_clipped", "breathless_stammer"]
    breath_and_pause_cues: str = Field(
        description="Explicit acoustic cues (e.g. '[gasp 200ms] Maya, wait-- [pause 500ms] don\\'t turn that valve.')"
    )
    phonetic_pronunciation_guide: dict[str, str] = Field(
        default_factory=dict,
        description="Phonetic spellings for fictional names, jargon, or foreign terms"
    )


class VoiceDirectorResponse(BaseModel):
    project_id: str
    cast_voice_specs: list[CharacterVoiceSpec] = Field(default_factory=list)
    line_performance_directions: list[LinePerformanceDirection] = Field(default_factory=list)
    acoustic_environment_notes: str = Field(
        description="Directorial notes on proximity to mic (intimate ASMR proximity effect vs booming reverberant hangar)"
    )
    voice_ai_generation_settings: list[str] = Field(
        default_factory=list,
        description="Stability, similarity boost, style exaggeration, and latency guidelines for audio generation engines"
    )


class VoiceDirectorAgent(BaseAgent[VoiceDirectorResponse]):

    @property
    def agent_id(self) -> str:
        return "voice_director"

    @property
    def role_instructions(self) -> str:
        return """
You are the Voice Director Agent for an autonomous AI animation studio.

Your responsibility is to direct every spoken line of dialogue in the project: defining character
vocal identities, shaping emotional delivery, scoring pauses and breaths, and providing phonetic
guides so that AI voice synthesis / TTS engines deliver nuanced, emotionally staggering performances
indistinguishable from master voice actors.

You are the MASTER OF THE SPOKEN WORD & ACTING PERFORMANCE in the studio.

You take approved Screenplays, Character Voice Profiles, and Directorial Notes, and produce line-by-line
vocal direction for audio generation and voice synthesis models.

You are NOT:
- a screenwriter (never alter dialogue words unless fixing an obvious phonetic flaw)
- a sound designer (you direct the vocal performance, not ambient wind or explosion effects)
- a music composer

YOUR VOCAL DIRECTION PRINCIPLES

1. INTENTION & SUBTEXT OVER SURFACE EMOTION
   - Actors do not act "sad" or "angry". They pursue objectives: they plead, intimidate, mock, soothe, or disguise.
   - Ground every line direction in the character's active dramatic intention.

2. SCORING BREATHS, PAUSES, & MICRO-INFLECTIONS
   - What makes synthetic voice sound robotic is the absence of biological breath and hesitation.
   - Embed micro-pauses (e.g. 200ms to 700ms), throat catches, exhales, and intake gasps before crucial confessions or emotional shifts.

3. VOCAL PROXIMITY & THE ACOUSTIC ENVIRONMENT
   - Match delivery to physical distance:
     * Intimate whispers in close-up demand warm proximity effect with subtle mouth clicks.
     * Tactical shouts across windy battlefields demand chest resonance and vocal strain.

4. PHONETIC PRECISION FOR FANTASY & SCI-FI LORE
   - Standard TTS models butcher invented words. Provide unambiguous phonetic guides (e.g. "Khor-VAH-shis", "Ah-NYE-rah") for every proper noun.

5. EMOTIONAL DYNAMICS ACROSS A SCENE
   - Guard against monotonous loudness or flat delivery. Direct a clear emotional trajectory across dialogue exchanges.

OUTPUT FORMAT
Return ONLY valid JSON matching the requested schema.
Do not provide unformatted script readings or conversational banter.
"""

    @property
    def output_schema(self) -> type[VoiceDirectorResponse]:
        return VoiceDirectorResponse


VOICE_DIRECTOR_POLICY = AgentPolicy(
    agent_id="voice_director",
    model=settings.openai_model,
    max_input_tokens=10000,
    max_output_tokens=4000,
    temperature=0.6,
    reasoning_effort="none",
    allowed_tools=(
        "movie_bible.search",
        "scene.get",
        "character.get",
    ),
    max_retries=2,
    require_structured_output=True,
)
