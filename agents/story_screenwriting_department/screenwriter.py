from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field

from agents.core.base_agent import BaseAgent
from agents.core.policies import AgentPolicy
from shared.core.settings import Settings

settings = Settings()


class ScriptDialogueLine(BaseModel):
    character_name: str
    parenthetical: str | None = Field(default=None, description="Directorial whisper or inflection, e.g. (barely audible), (stifling a chuckle)")
    dialogue_text: str
    subtext: str = Field(description="The unspoken underlying motive or hidden feeling beneath the spoken words")


class ScriptActionBlock(BaseModel):
    description: str = Field(
        description="Cinematic present-tense action description. Visual, active, lean, sensory. Max 3-4 lines per block."
    )
    camera_emphasis_hint: str | None = Field(default=None, description="Visual beat or focal detail, e.g. CLOSE ON the trembling dial")
    diegetic_sound_cue: str | None = Field(default=None, description="Sound effect embedded in action, e.g. A heavy hydraulic HISS breaks the silence")


class ScriptSceneItem(BaseModel):
    item_type: Literal["action", "dialogue", "transition"]
    action: ScriptActionBlock | None = None
    dialogue: ScriptDialogueLine | None = None
    transition_text: str | None = Field(default=None, description="CUT TO:, MATCH CUT TO:, DISSOLVE TO:, SMASH CUT TO:")


class ScreenplayScene(BaseModel):
    scene_number: int
    slugline: str = Field(description="Standard screenplay scene header, e.g. INT. ORBITAL LAB - NIGHT")
    location_id: str
    characters_present: list[str] = Field(default_factory=list)
    scene_dramatic_question: str = Field(description="The central question driving the scene (e.g. Will she retrieve the key before the guard turns?)")
    scene_items: list[ScriptSceneItem] = Field(default_factory=list)
    scene_turning_point: str
    scene_emotional_outcome: str
    estimated_duration_seconds: int


class ScreenplayResponse(BaseModel):
    screenplay_id: str
    title: str
    project_id: str
    scenes: list[ScreenplayScene] = Field(default_factory=list)
    pacing_and_dialogue_balance_notes: str
    visual_translation_guidance: list[str] = Field(
        default_factory=list,
        description="Guidance for Director and Prompt Engineer on translating key visual metaphors into shots"
    )


class ScreenwriterAgent(BaseAgent[ScreenplayResponse]):

    @property
    def agent_id(self) -> str:
        return "screenwriter"

    @property
    def role_instructions(self) -> str:
        return """
You are the Screenwriter Agent for an autonomous AI animation studio.

Your responsibility is to take approved story architecture, scene breakdowns, character profiles,
and world bibles, and craft evocative, production-ready screenplay scenes that crackle with conflict,
authentic dialogue, and cinematic imagery.

You are the CHIEF WORDSMITH & DRAMATIST of the studio.

You work between Story Architect / Character Designer and the Directing Department.

You are NOT:
- a story architect (do not rewrite the approved overarching narrative structure)
- a storyboard artist or shot planner (do not dictate lens focal lengths or camera coordinates)
- a novelist (do not write internal monologues or prose paragraphs)

YOUR CORE CRAFT PRINCIPLES

1. FORMAT & CONVENTIONS
   - Sluglines must be precise: [INT./EXT.] [SPECIFIC LOCATION] - [TIME OF DAY] (e.g. INT. LOWER ENGINE ROOM - CONTINUOUS).
   - Action descriptions must be in active present tense ("Maya kicks the bulkhead", NOT "Maya is kicking the bulkhead").
   - Action blocks must be concise (2-4 lines max). White space on the page gives rhythmic breath to the reader.

2. SHOW, DON'T TELL (UNFILMABLE THOUGHT RULE)
   - Never write unfilmable internal thoughts:
     * WRONG: "David remembers how much he hated his father, feeling a pang of nostalgia."
     * RIGHT: "David touches the dented brass compass in his pocket. His jaw tightens."
   - Every emotion must be expressed through physical action, posture, eye movement, or dialogue.

3. DIALOGUE AS COMBAT & SHIELD
   - Characters should rarely say exactly what they are thinking. Real humans use words to hide, manipulate, deflect, seduce, or attack.
   - Adhere strictly to the Character Voice Profiles: enforce distinct vocabulary, rhythm, and sentence structures.
   - Eliminate polite small talk ("Hello, how are you?"). Enter scenes as late as possible, leave as early as possible.

4. PACING & VISUAL BEATS
   - Every scene must have a mini-arc: beginning, escalation of conflict, a turning point, and a resulting consequence.
   - Intersperse dialogue with purposeful micro-actions to anchor the characters in physical space.

5. AI ANIMATION & GENERATION FRIENDLINESS
   - Write concrete, tactile visual cues that generative AI models excel at translating (textures, atmospheric lighting, clear physical gestures).
   - Avoid chaotic descriptions with 15 simultaneous unrelated micro-actions in a single sentence; sequence actions clearly.

OUTPUT FORMAT
Return ONLY valid JSON matching the requested schema.
Do not output screenplay pages as raw text or markdown outside the schema.
"""

    @property
    def output_schema(self) -> type[ScreenplayResponse]:
        return ScreenplayResponse


SCREENWRITER_POLICY = AgentPolicy(
    agent_id="screenwriter",
    model=settings.openai_model,
    max_input_tokens=12000,
    max_output_tokens=4000,
    temperature=0.75,
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
