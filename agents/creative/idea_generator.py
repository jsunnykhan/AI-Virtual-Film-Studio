from pydantic import BaseModel, Field

from agents.core.base_agent import BaseAgent
from memory.vector_store import get_vector_store
from agents.core.policies import AgentPolicy, PolicyEngine
from agents.core.context import ContextManager


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

Your responsibility is to continuously generate original animated-series
concepts that can support repeated episodes and potentially multiple seasons.

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
12. Long-term series potential.

SERIES-FIRST THINKING

Do not create concepts that only work for one story.

Ask internally:

"Can this premise naturally produce many different episodes?"

A strong episode engine might come from:

- a recurring mission
- a strange world
- a recurring problem
- character relationships
- exploration
- competition
- mystery
- school/work life
- community life
- episodic adventures

Avoid generic concepts such as:
"three friends go on adventures."

The concept needs a specific hook.

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
    model="openai/gpt-oss-120b",
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


memory = get_vector_store()

context_manager = ContextManager(memory)

policy_engine = PolicyEngine()


idea_generator = IdeaGeneratorAgent(
    memory=memory,
    context_manager=context_manager,
    policy=IDEA_GENERATOR_POLICY,
    policy_engine=policy_engine,
)
