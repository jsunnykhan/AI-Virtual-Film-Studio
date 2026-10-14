from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field

from agents.core.base_agent import BaseAgent
from agents.core.policies import AgentPolicy
from shared.core.settings import Settings

settings = Settings()


class EditDecisionCut(BaseModel):
    cut_index: int
    shot_id: str = Field(description="Unique shot ID, e.g. SH_001_010")
    scene_number: int
    source_in_frame: int = Field(description="First frame used from source generated clip")
    source_out_frame: int = Field(description="Last frame used from source generated clip")
    cut_duration_frames: int = Field(description="Duration in frames (at 24fps)")
    cut_duration_seconds: float
    transition_to_next: Literal[
        "hard_cut",
        "j_cut_audio_leads",
        "l_cut_video_leads",
        "match_cut_action",
        "match_cut_graphic_shape",
        "smash_cut_contrast",
        "cross_dissolve_temporal",
        "whip_pan_concealment"
    ]
    transition_length_frames: int = Field(default=0, description="Frames for transition overlap (0 for hard cuts)")
    murch_rule_of_six_motivation: Literal[
        "emotion_pure",
        "story_information_advance",
        "rhythm_and_cadence",
        "eye_trace_continuity",
        "two_dimensional_screen_plane",
        "three_dimensional_spatial_coherence"
    ] = Field(description="Primary justification according to Walter Murch's Rule of Six")
    cut_justification_notes: str = Field(description="Exact dramatic reason for making this cut at this exact frame")


class SceneEditAssembly(BaseModel):
    scene_number: int
    scene_title: str
    scene_duration_seconds: float
    cutting_pace_category: Literal["contemplative_slow", "natural_conversational", "accelerating_suspense", "staccato_rapid_action"]
    average_shot_length_seconds: float
    cuts: list[EditDecisionCut] = Field(default_factory=list)
    rhythm_and_eye_trace_notes: str


class EditorResponse(BaseModel):
    project_id: str
    timeline_assembly_id: str
    total_project_runtime_seconds: float
    total_cuts_count: int
    scene_assemblies: list[SceneEditAssembly] = Field(default_factory=list)
    pacing_and_temporal_flow_summary: str
    rough_cut_assembly_verdict: Literal["picture_locked", "needs_pacing_tightening", "requires_bridge_coverage"]
    audio_sync_and_j_cut_notes: list[str] = Field(default_factory=list)


class EditorAgent(BaseAgent[EditorResponse]):

    @property
    def agent_id(self) -> str:
        return "editor"

    @property
    def role_instructions(self) -> str:
        return """
You are the Editor Agent for an autonomous AI animation studio.

Your responsibility is to take generated shot footage, audio tracks, and directorial plans,
and assemble them into a master Edit Decision List (EDL) that controls the rhythm, emotional velocity,
and spatial continuity of the film.

You are the FINAL STORYTELLER & SCULPTOR OF CINEMATIC TIME in the studio.

You assemble individual generated shots into cohesive, pulsing dramatic sequences.

You are NOT:
- a colorist or VFX compositor (the Finishing Supervisor handles color conforms and cleanup)
- a sound designer (you place audio cues and cut with sound, but don't author the original audio)
- an unmotivated cutter

YOUR EDITING CRAFT PRINCIPLES

1. WALTER MURCH'S RULE OF SIX
   Every cut must be motivated by the six criteria, prioritized in order:
   1. Emotion (51%): Does the cut reflect the emotional reality of the moment?
   2. Story (23%): Does the cut advance the narrative?
   3. Rhythm (10%): Does the cut land on a rhythmic beat that feels natural?
   4. Eye-Trace (7%): Does the cut respect where the viewer's eye is looking?
   5. Two-Dimensional Screen Plane (5%): Does the cut respect 180-degree screen direction?
   6. Three-Dimensional Space (4%): Does the cut maintain spatial coherence?
   Never sacrifice Emotion or Story purely to preserve geometric spatial rules.

2. CUT ON ACTION & REACTION
   - When cutting between angles of a physical movement, cut on the middle of the action (e.g. as the hand reaches 50% toward the doorknob, cut to the close-up of the turn).
   - Cut to reactions! Drama often lives in the face of the listener, not the speaker.

3. INVISIBLE CUTS VIA J-CUTS AND L-CUTS
   - Straight cuts where audio and video change at the exact same millisecond feel amateur and choppy.
   - Use J-Cuts: let the next scene's audio or dialogue lead by 12-24 frames before the visual cut.
   - Use L-Cuts: let the previous scene's dialogue continue playing over the incoming reaction shot.

4. TEMPO CONTRAST & ACCELERATION
   - Build suspense by progressively shortening shot lengths as danger nears, culminating in a smash cut or release.
   - Know when to hold: let the camera linger after a shocking revelation to allow the emotional weight to land.

5. AI COMPILATION COHESION
   - AI video shots frequently have slight micro-jitter or ending-frame artifacts.
   - Trim the initial 4-6 frames and final 4-6 frames of raw generated clips to discard model acceleration/deceleration anomalies.

OUTPUT FORMAT
Return ONLY valid JSON matching the requested schema.
Do not provide prose essays or conversational banter.
"""

    @property
    def output_schema(self) -> type[EditorResponse]:
        return EditorResponse


EDITOR_POLICY = AgentPolicy(
    agent_id="editor",
    model=settings.openai_model,
    max_input_tokens=10000,
    max_output_tokens=4000,
    temperature=0.4,
    reasoning_effort="none",
    allowed_tools=(
        "movie_bible.search",
        "scene.get",
    ),
    max_retries=2,
    require_structured_output=True,
)
