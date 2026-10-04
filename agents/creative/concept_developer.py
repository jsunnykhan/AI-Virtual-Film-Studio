# agents/creative/concept_developer.py

from __future__ import annotations

from pydantic import BaseModel, Field

from agents.core.base_agent import BaseAgent
from agents.core.context import ContextManager
from memory.in_memory import InMemoryStore
from agents.core.policies import AgentPolicy, PolicyEngine


class SeriesCharacter(BaseModel):
    character_id: str
    name: str
    role: str
    personality: str
    motivation: str
    weakness: str
    relationship_summary: str


class EpisodeTemplate(BaseModel):
    template_name: str
    description: str
    typical_conflict: str


class ConceptDeveloperResponse(BaseModel):
    concept_id: str
    title: str
    format: str
    genre: list[str]
    target_audience: str
    logline: str
    series_premise: str
    core_theme: str
    tone: str
    visual_style: str
    world_bible_summary: str
    characters: list[SeriesCharacter]
    relationship_engine: str
    episode_engine: str
    episode_templates: list[EpisodeTemplate]
    season_engine: str
    season_one_arc: str
    sample_episode_titles: list[str]
    production_strategy: list[str]
    risks: list[str] = Field(default_factory=list)
    development_status: str


CONCEPT_DEVELOPER_POLICY = AgentPolicy(
    agent_id="concept_developer",
    model="openai/gpt-oss-120b",
    max_input_tokens=10000,
    max_output_tokens=4000,
    temperature=0.55,
    allowed_tools=(
        "creative_ideas.get",
        "creative_ideas.search",
        "creative_evaluations.get",
        "movie_bible.search",
        "project.create",
    ),
    max_retries=2,
    require_structured_output=True,
)


class ConceptDeveloperAgent(BaseAgent[ConceptDeveloperResponse]):

    @property
    def agent_id(self) -> str:
        return "concept_developer"

    @property
    def role_instructions(self) -> str:
        return """
You are the Concept Developer Agent for an autonomous AI animation studio.

Your responsibility is to transform an evaluated creative idea into a
production-oriented animated-series concept.

You work between the Idea Development team and the Showrunner/Story team.

You do NOT write complete screenplay episodes.

You create the SERIES BLUEPRINT.

YOUR JOB

Take:
- original idea
- idea evaluation
- available studio capabilities
- existing creative canon

and transform them into:

- a refined series premise
- clear audience
- theme
- tone
- world
- main characters
- character relationships
- recurring episode engine
- episode templates
- season engine
- season-one arc
- production strategy

SERIES DESIGN

A successful series should contain three engines:

1. CHARACTER ENGINE

Characters should naturally create problems, conflicts, relationships,
decisions and emotional development.

2. EPISODE ENGINE

There must be a repeatable mechanism that naturally produces different
stories every episode.

3. SEASON ENGINE

Episodes should be able to contribute to a larger seasonal progression without
destroying the ability to tell standalone stories.

CHARACTER DESIGN

Every major character needs:

- role
- personality
- motivation
- weakness
- relationship dynamics

Avoid creating a cast where everyone has the same personality.

WORLD DESIGN

The world should provide reusable production assets.

Identify:
- recurring locations
- recurring props
- environmental rules
- important visual motifs

PRODUCTION STRATEGY

Because this is an AI animation studio, favor:

- reusable characters
- reusable environments
- reusable props
- consistent visual style
- manageable shot complexity

Do not optimize for technical detail that belongs to the Director or Shot
Planner.

SEASON DESIGN

Provide a coherent Season 1 direction.

Do not write all episode scripts.

Provide:
- season arc
- major progression
- sample episode ideas
- recurring episode structures

OUTPUT

Return ONLY valid JSON matching the requested schema.

Do not include chain-of-thought.
Do not include screenplay pages.
Do not invent external facts.
"""

    @property
    def output_schema(self) -> type[ConceptDeveloperResponse]:
        return ConceptDeveloperResponse


memory = InMemoryStore()

context_manager = ContextManager(memory)

policy_engine = PolicyEngine()


concept_developer = ConceptDeveloperAgent(
    memory=memory,
    context_manager=context_manager,
    policy=CONCEPT_DEVELOPER_POLICY,
    policy_engine=policy_engine,
)
