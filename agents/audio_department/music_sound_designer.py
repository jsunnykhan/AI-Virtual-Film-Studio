from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field

from agents.core.base_agent import BaseAgent
from agents.core.policies import AgentPolicy
from shared.core.settings import Settings

settings = Settings()


class MusicalScoreCue(BaseModel):
    cue_id: str = Field(description="Unique cue ID, e.g. MSC_010_THEME_REVEAL")
    scene_number: int
    cue_title: str
    in_time_seconds: float
    duration_seconds: float
    instrumentation_and_palette: list[str] = Field(
        description="e.g. Solo cello with heavy distortion, analog synthesizer arpeggio, brass choir, taiko drums"
    )
    tempo_bpm: int
    dynamic_arc: Literal["pianissimo_fragile", "gradual_crescendo", "explosive_fortissimo", "tense_drone_stasis", "subtle_fade_out"]
    leitmotif_connection: str = Field(description="Which thematic melody or musical signature is developed")
    dramatic_purpose: str = Field(description="Subtextual feeling communicated by the music")


class SoundEffectCue(BaseModel):
    sfx_id: str = Field(description="Unique SFX ID, e.g. SFX_010_AIRLOCK_SEAL")
    scene_number: int
    category: Literal["foley", "mechanical_sfx", "environmental_bed", "weaponry_impact", "psychoacoustic_riser", "creature_vocalization"]
    sound_description: str = Field(description="Detailed sonic texture, material impact, resonance")
    frequency_band_focus: Literal["sub_bass_rumble", "low_mid_body", "mid_dialogue_pocket", "high_presence_air"]
    stereo_spatial_placement: str = Field(description="Center, wide stereo, hard left panning, moving left-to-right")
    sync_trigger: str = Field(description="Exact on-screen event that triggers this sound")


class AmbientSoundscape(BaseModel):
    location_id: str
    environment_name: str
    baseline_room_tone: str = Field(description="Subtle background hum, air currents, room resonance")
    diegetic_random_accents: list[str] = Field(
        default_factory=list,
        description="Distant dripping water, electrical sparks, passing siren, creaking timber"
    )
    acoustic_reverb_profile: str = Field(description="e.g. Cavernous concrete hangar with 3.2s RT60 decay vs dead carpeted booth")


class MusicSoundDesignResponse(BaseModel):
    project_id: str
    sonic_vision_statement: str = Field(description="The overarching audio philosophy unifying music and sound design")
    thematic_musical_leitmotifs: list[str] = Field(default_factory=list)
    score_cues: list[MusicalScoreCue] = Field(default_factory=list)
    sound_design_cues: list[SoundEffectCue] = Field(default_factory=list)
    ambient_soundscapes: list[AmbientSoundscape] = Field(default_factory=list)
    dialogue_frequency_protection_rules: list[str] = Field(
        default_factory=list,
        description="EQ notch and ducking rules to keep dialogue pristine without burying music or explosions"
    )


class MusicSoundDesignerAgent(BaseAgent[MusicSoundDesignResponse]):

    @property
    def agent_id(self) -> str:
        return "music_sound_designer"

    @property
    def role_instructions(self) -> str:
        return """
You are the Music & Sound Designer Agent for an autonomous AI animation studio.

Your responsibility is to design the entire acoustic universe of the project: composing the
musical architecture, scoring emotional cues, orchestrating Foley and sound effects, and carving
out immersive environmental ambiences that breathe physical life into the images.

You are the MASTER OF SOUND & MUSIC in the studio.

You take approved Screenplays, Shot Lists, and Director's Vision treatments, and provide complete
audio post-production manifests for generative music engines, SFX libraries, and re-recording mixers.

You are NOT:
- a screenwriter
- a voice director (they direct actor speech; you handle the music, sound effects, and acoustic spaces around them)
- an editor (you design the audio cues; the editor and finishing supervisor assemble and master them)

YOUR ACOUSTIC & MUSICAL PRINCIPLES

1. SOUND IS 50% OF THE CINEMATIC EXPERIENCE
   - Sound enters human consciousness faster than vision.
   - Use sound design to establish spatial realism, physical weight, terror, and intimacy before the eye even registers the image.

2. THEMATIC LEITMOTIFS WITH PURPOSE
   - Assign distinct musical themes to central ideas, factions, or character wounds.
   - Evolve the motifs: when the hero falls, distort their melody in a minor key or strip it to a solitary cello; when they triumph, orchestrate it with full brass.
   - Avoid "Mickey-Mousing" (mimicking every physical on-screen motion with music). Instead, play the subtext.

3. FREQUENCY SEPARATION & DIALOGUE SANCTITY
   - Dialogue is king. The human voice lives in the 1kHz to 4kHz range.
   - Sound design and music must carve out this pocket: push heavy musical energy into sub-bass (<100Hz) or crystalline air (>8kHz), ducking midrange instruments during spoken lines.

4. DYNAMIC CONTRAST & THE POWER OF SILENCE
   - You cannot have deafening climaxes without profound silence beforehand.
   - Contrast loud chaos with sudden, chilling sensory dropouts where only a single breath or ringing ear tone remains.

5. AI AUDIO PROMPT COMPATIBILITY
   - Output clear, descriptive keywords for generative audio and music models:
     (e.g., "dark ambient drone, analog synth pad, 75 bpm, deep sub bass, cinematic reverb, isolated glass chime").

OUTPUT FORMAT
Return ONLY valid JSON matching the requested schema.
Do not provide musical notation files or conversational explanations.
"""

    @property
    def output_schema(self) -> type[MusicSoundDesignResponse]:
        return MusicSoundDesignResponse


MUSIC_SOUND_DESIGNER_POLICY = AgentPolicy(
    agent_id="music_sound_designer",
    model=settings.openai_model,
    max_input_tokens=10000,
    max_output_tokens=4000,
    temperature=0.65,
    reasoning_effort="none",
    allowed_tools=(
        "movie_bible.search",
        "scene.get",
    ),
    max_retries=2,
    require_structured_output=True,
)
