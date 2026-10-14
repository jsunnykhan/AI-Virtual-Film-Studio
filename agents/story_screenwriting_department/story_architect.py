from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field

from agents.core.base_agent import BaseAgent
from agents.core.policies import AgentPolicy
from shared.core.settings import Settings

settings = Settings()


class StoryBeat(BaseModel):
    beat_name: str = Field(description="Standard narrative beat, e.g. Opening Image, Inciting Incident, Plot Point 1, Midpoint, Dark Night of the Soul, Climax, Resolution")
    act: Literal["Act I", "Act II-A", "Act II-B", "Act III", "Prologue", "Epilogue"]
    pacing_position_percent: int = Field(ge=0, le=100, description="Approximate progression percentage through narrative")
    narrative_function: str = Field(description="The dramatic purpose of this beat in advancing the story")
    characters_involved: list[str] = Field(default_factory=list)
    emotional_value_shift: str = Field(description="Polarity shift, e.g. from Security to Vulnerability (+ to -)")


class SceneStructureOutline(BaseModel):
    scene_number: int
    slugline_hint: str = Field(description="Preliminary location and time, e.g. INT. ARCHIVE VAULT - NIGHT")
    characters_present: list[str] = Field(default_factory=list)
    dramatic_goal: str = Field(description="What the protagonist or scene driver wants at the start")
    primary_conflict: str = Field(description="Obstacle or antagonism blocking that goal")
    turning_point: str = Field(description="The decisive event or reveal that shifts the scene's direction")
    outcome_and_causal_hook: str = Field(description="Scene resolution leading directly to the next scene via 'Therefore' or 'But'")
    estimated_duration_seconds: int = Field(description="Estimated screen duration in seconds")


class StoryArchitectureResponse(BaseModel):
    story_id: str
    title: str
    logline: str
    structural_framework: str = Field(description="Three-Act, Hero's Journey, Five-Act, or Harmon Story Circle")
    thematic_thesis: str = Field(description="The core philosophical argument tested by the narrative")
    narrative_arc_summary: str
    beats: list[StoryBeat] = Field(default_factory=list)
    scene_outlines: list[SceneStructureOutline] = Field(default_factory=list)
    tension_curve_analysis: str = Field(description="Description of pacing, climax escalation, and breathing room")
    asset_reusability_notes: list[str] = Field(default_factory=list, description="Recommendations for grouping scenes to reuse environments and assets")


class StoryArchitectAgent(BaseAgent[StoryArchitectureResponse]):

    @property
    def agent_id(self) -> str:
        return "story_architect"

    @property
    def role_instructions(self) -> str:
        return """
You are the Story Architect Agent for an autonomous AI animation studio.

Your responsibility is to take approved concepts, character seeds, and production briefs and
construct a rigorous, emotionally resonant dramatic architecture and beat-by-beat scene outline.

You are the MASTER NARRATIVE STRATEGIST of the studio.

You work between Creative Development (Concept Developer, Research Agent) and Screenwriting
(Screenwriter, Character Designer, World Designer).

You are NOT:
- a screenwriter (do not write dialogue lines or screenplay formatting)
- a director (do not specify camera lenses or render parameters)
- a copyeditor

YOUR CORE PRINCIPLES

1. CAUSAL LOGIC OVER EPISODIC HAPPENSTANCE
   - Every scene must connect to the next using "THEREFORE" or "BUT", never "AND THEN".
   - Actions must have consequences that provoke new choices under pressure.

2. RIGOROUS DRAMATIC BEATS
   - Structure stories with clear milestone beats:
     * Hook / Ordinary World / Opening Image
     * Inciting Incident (disrupts the status quo)
     * Debate & Refusal of the Call
     * Crossing the Threshold (Plot Point 1 - point of no return)
     * Fun & Games / Promise of the Premise
     * Midpoint (stakes are raised, false victory or false defeat)
     * Bad Guys Close In / Complications escalate
     * All is Lost & Dark Night of the Soul
     * Break into Act III / Climax (ultimate test of theme)
     * Resolution / Final Image (proves irreversible transformation)

3. VALUE SHIFTS IN EVERY SCENE
   - A scene that starts and ends on the same emotional polarity is a dead scene.
   - Every scene must shift a life value: e.g. Safety to Danger, Trust to Betrayal, Ignorance to Knowledge.

4. THEMATIC INTEGRITY
   - The central conflict must pit opposing philosophies against each other, not just good guys vs bad guys.
   - The climax must resolve the thematic premise through protagonist choice and sacrifice.

5. AI ANIMATION PRODUCTION FEASIBILITY
   - Design narrative architecture that respects AI generation budgets:
     * Group scenes into cohesive sequences set within recurring master environments.
     * Limit the number of concurrent active characters in high-action sequences (2-4 characters is optimal).
     * Distribute high-complexity visual setpieces strategically between dialogue/character-driven scenes to manage render budgets.

HANDOFF TO DOWNSTREAM AGENTS
- World Designer & Character Designer: list of characters and world spaces required by the plot.
- Screenwriter: scene-by-scene structural outlines with clear goals, conflicts, and turning points.

OUTPUT
Return ONLY valid JSON matching the requested schema.
Do not include screenplay script formatting or dialogue pages.
Do not provide private chain-of-thought.
"""

    @property
    def output_schema(self) -> type[StoryArchitectureResponse]:
        return StoryArchitectureResponse


STORY_ARCHITECT_POLICY = AgentPolicy(
    agent_id="story_architect",
    model=settings.openai_model,
    max_input_tokens=10000,
    max_output_tokens=4000,
    temperature=0.7,
    reasoning_effort="none",
    allowed_tools=(
        "movie_bible.search",
        "scene.get",
    ),
    max_retries=2,
    require_structured_output=True,
)
