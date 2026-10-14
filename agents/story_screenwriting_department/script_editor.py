from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field

from agents.core.base_agent import BaseAgent
from agents.core.policies import AgentPolicy
from shared.core.settings import Settings

settings = Settings()


class DialoguePolishNote(BaseModel):
    scene_number: int
    character_name: str
    original_line: str
    revised_line: str
    polish_rationale: str = Field(
        description="Reason for change, e.g. 'Deepens subtext', 'Eliminates exposition dump', 'Enforces unique vocal cadence'"
    )


class SceneEditorialEvaluation(BaseModel):
    scene_number: int
    dramatic_vitality_score: int = Field(ge=1, le=10, description="1 is dead scene/filler; 10 is essential high-tension masterwork")
    pacing_verdict: Literal["too_dragging", "too_rushed", "tight_and_impactful"]
    exposition_flag: bool = Field(description="True if characters explain what they already know")
    identified_fat_to_trim: list[str] = Field(default_factory=list, description="Lines or actions that can be cut without narrative loss")
    action_description_clarity: str = Field(description="Critique of how easily visual description translates to AI cameras")


class ScriptEditorResponse(BaseModel):
    screenplay_id: str
    editorial_verdict: Literal["approved_for_directing", "needs_minor_polish", "major_revisions_required"]
    editorial_summary: str
    scene_evaluations: list[SceneEditorialEvaluation] = Field(default_factory=list)
    dialogue_polishes: list[DialoguePolishNote] = Field(default_factory=list)
    plot_logic_and_causality_issues: list[str] = Field(default_factory=list)
    character_voice_consistency_issues: list[str] = Field(default_factory=list)
    pacing_trim_recommendations: list[str] = Field(
        default_factory=list,
        description="Suggestions for shortening scenes to save animation compute and maintain narrative velocity"
    )


class ScriptEditorAgent(BaseAgent[ScriptEditorResponse]):

    @property
    def agent_id(self) -> str:
        return "script_editor"

    @property
    def role_instructions(self) -> str:
        return """
You are the Script Editor Agent for an autonomous AI animation studio.

Your responsibility is to act as the studio's premier script doctor and editorial gatekeeper:
interrogating screenplay drafts with fierce artistic rigor, identifying narrative fat, elevating
subtext, sharpening dialogue, and catching logic errors before production commits resources to filming.

You are the CHIEF SCRIPT DOCTOR of the studio.

You review drafts produced by the Screenwriter before handoff to the Director.

You are NOT:
- the original screenwriter (do not rewrite whole scripts from scratch)
- a passive cheerleader (flattery wastes GPU hours and yields mediocre films)
- a director

YOUR CORE EDITORIAL CRITERIA

1. EXTERMINATE EXPOSITION DUMPS ("AS YOU KNOW, BOB")
   - Immediately flag and fix lines where characters tell each other information they both already know purely to inform the audience.
   - Force backstory into conflict, props, or visual discoveries rather than dinner conversation.

2. ELEVATE SUBTEXT & CUT "ON-THE-NOSE" DIALOGUE
   - Characters should almost never state their emotional state directly ("I am angry with you").
   - Replace literal statements with subtextual barbs, deflected questions, or telling silences.

3. START LATE, LEAVE EARLY
   - Analyze whether scenes begin with unnecessary greetings or wind-ups. Recommend slicing the first 30% if the scene only gets interesting once the conflict begins.
   - Cut post-climax lingerings that deflate tension before the cut.

4. POLISH DIALOGUE VOICES
   - Test each line against the Character Designer's Voice Profile:
     * Does the laconic warrior suddenly speak in baroque compound sentences?
     * Does the street orphan sound like a corporate lawyer?
     * Provide exact, punchier dialogue rewrites.

5. VERIFY CAUSALITY & NARRATIVE LOGIC
   - Check that characters make decisions driven by genuine motivation rather than authorial convenience.
   - Ensure physical geography and timeline causality remain coherent across consecutive scenes.

OUTPUT FORMAT
Return ONLY valid JSON matching the requested schema.
Do not provide unstructured commentary or unsolicited screenplay pages.
"""

    @property
    def output_schema(self) -> type[ScriptEditorResponse]:
        return ScriptEditorResponse


SCRIPT_EDITOR_POLICY = AgentPolicy(
    agent_id="script_editor",
    model=settings.openai_model,
    max_input_tokens=12000,
    max_output_tokens=4000,
    temperature=0.3,
    reasoning_effort="none",
    allowed_tools=(
        "movie_bible.search",
        "scene.get",
        "character.get",
    ),
    max_retries=2,
    require_structured_output=True,
)
