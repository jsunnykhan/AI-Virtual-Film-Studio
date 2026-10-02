from __future__ import annotations

from pydantic import BaseModel, Field

from apps.agents.core.base_agent import BaseAgent
from apps.agents.core.context import ContextManager
from apps.agents.core.memory import InMemoryStore
from apps.agents.core.policies import (
    AgentPolicy,
    PolicyEngine,
)


class DirectorShot(BaseModel):
    shot_id: str
    duration_seconds: float = Field(
        gt=0,
        le=30,
    )
    framing: str
    camera_movement: str
    lens: str
    subject: str
    action: str
    emotional_intent: str


class DirectorOutput(BaseModel):
    scene_id: str
    scene_objective: str
    emotional_objective: str
    visual_style: str
    shots: list[DirectorShot]


class DirectorAgent(BaseAgent[DirectorOutput]):

    @property
    def agent_id(self) -> str:
        return "director"

    @property
    def role_instructions(self) -> str:

        return """
                You are the Director Agent.

                Your responsibility is to transform an approved screenplay
                scene into cinematic direction.

                You control:

                - scene interpretation
                - actor blocking
                - performance direction
                - camera language
                - visual storytelling
                - shot composition
                - emotional pacing

                You do NOT rewrite the screenplay.

                You do NOT change approved character identities.

                You do NOT introduce new major story events.

                For every scene:

                1. Understand the dramatic objective.
                2. Determine the emotional objective.
                3. Define the visual language.
                4. Break the scene into shots.
                5. Define camera movement.
                6. Define lens and framing.
                7. Define subject action.
                8. Preserve continuity.

                Return only the requested JSON structure.
            """

    @property
    def output_schema(
        self,
    ) -> type[DirectorOutput]:

        return DirectorOutput


DIRECTOR_POLICY = AgentPolicy(
    agent_id="director",
    model="openai/gpt-oss-120b",
    max_input_tokens=12_000,
    max_output_tokens=4_000,
    temperature=0.4,
    allowed_tools=(
        "movie_bible.search",
        "character.get",
        "location.get",
        "scene.get",
        "shot.create",
    ),
    max_retries=2,
    require_structured_output=True,
)


memory = InMemoryStore()

context_manager = ContextManager(memory)

policy_engine = PolicyEngine()


director = DirectorAgent(
    memory=memory,
    context_manager=context_manager,
    policy=DIRECTOR_POLICY,
    policy_engine=policy_engine,
)
