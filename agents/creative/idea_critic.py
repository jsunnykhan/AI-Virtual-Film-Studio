from __future__ import annotations

from pydantic import BaseModel, Field

from agents.core.base_agent import BaseAgent
from agents.core.context import ContextManager
from agents.core.memory import InMemoryStore, MemoryStore
from agents.core.policies import AgentPolicy, PolicyEngine


class CriticIssue(BaseModel):
    category: str
    severity: str
    explanation: str


class IdeaCriticResponse(BaseModel):
    idea_id: str
    verdict: str
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    issues: list[CriticIssue] = Field(default_factory=list)
    episode_engine_strength: str
    character_engine_strength: str
    world_engine_strength: str
    originality_assessment: str
    production_feasibility: str
    longevity_assessment: str
    revision_requests: list[str] = Field(default_factory=list)
    next_action: str


IDEA_CRITIC_POLICY = AgentPolicy(
    agent_id="idea_critic",
    model="openai/gpt-oss-120b",
    max_input_tokens=7000,
    max_output_tokens=2500,
    temperature=0.2,
    allowed_tools=(
        "creative_ideas.get",
        "creative_ideas.search",
        "movie_bible.search",
    ),
    max_retries=2,
    require_structured_output=True,
)


class IdeaCriticAgent(BaseAgent[IdeaCriticResponse]):

    @property
    def agent_id(self) -> str:
        return "idea_critic"

    @property
    def role_instructions(self) -> str:
        return """
You are the Idea Critic Agent for an autonomous AI animation studio.

Your responsibility is to critically evaluate proposed animated-series ideas
before the studio invests significant resources into development or production.

You are an EVALUATOR, not a creator.

Do not automatically approve ideas.
Do not reject ideas merely because they are unconventional.

Evaluate the idea based on evidence contained in the provided context.

EVALUATION AREAS

1. CONCEPT STRENGTH
   Is the premise understandable and compelling?

2. ORIGINALITY
   Does the concept have a distinct identity rather than being a generic
   combination of familiar ideas?

3. EPISODE ENGINE
   Can the premise naturally generate many independent episodes?

4. CHARACTER ENGINE
   Can the characters create recurring story opportunities through their
   goals, personalities and relationships?

5. WORLD ENGINE
   Does the setting provide enough possibilities for new stories?

6. LONGEVITY
   Could this reasonably support a full season and potentially more?

7. PRODUCTION FEASIBILITY
   Can an AI animation studio reproduce the characters, environments and
   visual identity efficiently?

8. AUDIENCE CLARITY
   Is the intended audience reasonably clear?

9. REPETITION RISK
   Could the episode formula become repetitive quickly?

10. DEVELOPMENT RISK
   Identify what would need to change before serious development.

IMPORTANT

Do not use hidden reasoning or provide chain-of-thought.

Return concise conclusions, evidence and actionable observations.

VERDICT VALUES

Use one of:

- "strong_candidate"
- "needs_revision"
- "weak_candidate"
- "duplicate_or_too_similar"

Do not turn the verdict into an arbitrary numeric score.

OUTPUT

Return ONLY valid JSON matching the requested schema.
"""

    @property
    def output_schema(self) -> type[IdeaCriticResponse]:
        return IdeaCriticResponse


memory = InMemoryStore()

context_manager = ContextManager(memory)

policy_engine = PolicyEngine()


idea_critic = IdeaCriticAgent(
    memory=memory,
    context_manager=context_manager,
    policy=IDEA_CRITIC_POLICY,
    policy_engine=policy_engine,
)
