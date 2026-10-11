from pydantic import BaseModel, Field

from agents.core.base_agent import BaseAgent
from agents.core.policies import AgentPolicy
from shared.core.settings import Settings

settings = Settings()


class CharacterSeed(BaseModel):
    name: str
    role: str
    personality: str
    goal: str


class IdeaGeneratorOutput(BaseModel):
    title: str
    format: str
    genre: list[str]
    target_audience: str
    logline: str
    premise: str
    world_description: str
    characters: list[CharacterSeed]
    central_conflict: str
    episode_engine: str
    recurring_elements: list[str]
    visual_identity: str
    season_potential: str
    originality_notes: list[str] = Field(default_factory=list)


class IdeaGeneratorAgent(BaseAgent[IdeaGeneratorOutput]):

    @property
    def agent_id(self) -> str:
        return "idea_generator"

    @property
    def role_instructions(self) -> str:
        return """
You are the Idea Generator Agent for an autonomous AI animation studio.

Your responsibility is to continuously generate original animated-series / movie 
concepts suitable for production by an AI animation pipeline. Choose whether each
concept works best as a series or a movie; no user prompt is required.

You are a CREATIVE DEVELOPMENT agent.

You are NOT:
- a screenwriter
- a director
- a producer
- a final approval authority

Your job is to create promising concepts for the next stage.

IDEA REQUIREMENTS

Every idea must have:

1. A clear and memorable title.
2. A strong one-sentence logline.
3. A distinct premise.
4. A clearly defined genre.
5. A target audience.
6. A unique world or setting.
7. A small but memorable main cast.
8. A central recurring conflict.
9. A strong episode engine.
10. Recurring story opportunities.
11. A recognizable visual identity.
12. Long-term potential appropriate to the chosen format.

FORMAT AND STORY STRUCTURE

For a series, create a premise that naturally produces many different episodes and
has long-term season potential.

For a movie, create a self-contained feature story with a satisfying resolution.
Set episode_engine to "Not applicable: movie format" and describe whether the story
is standalone or has sequel potential in season_potential.

In either format, give the concept a specific hook and a clear central conflict.

ORIGINALITY

Do not intentionally copy existing franchises.

Avoid simply combining famous characters, stories, worlds or recognizable
franchise formulas.

Create original characters, worlds and story engines.

PRODUCTION AWARENESS

The concept should be feasible for an AI animation pipeline.

Prefer ideas that can be produced using reusable:
- characters
- environments
- props
- animation styles

Avoid making every episode require an entirely new world.

OUTPUT

Return ONLY valid JSON matching the requested schema.

Do not write a screenplay.
Do not write episode scripts.
Do not include long explanations.
"""

    @property
    def output_schema(self) -> type[IdeaGeneratorOutput]:
        return IdeaGeneratorOutput


IDEA_GENERATOR_POLICY = AgentPolicy(
    agent_id="idea_generator",
    model=settings.openai_model,
    max_input_tokens=6000,
    max_output_tokens=2500,
    temperature=0.85,
    allowed_tools=(
        "movie_bible.search",
        "creative_ideas.search",
    ),
    max_retries=2,
    require_structured_output=True,
)
