from agents.creative_development.research_agent import (
    ResearchAgent,
    research_agent_policy,
)
from agents.executive_department.executive_producer import (
    EXECUTIVE_PRODUCER_POLICY,
    ExecutiveProducerAgent,
)
from memory.vector_store import get_vector_store
from agents.core.context import ContextManager
from agents.core.policies import PolicyEngine

from agents.creative_development.idea_generator import (
    IdeaGeneratorAgent,
    IDEA_GENERATOR_POLICY,
)
from agents.creative_development.idea_critic import IdeaCriticAgent, IDEA_CRITIC_POLICY
from agents.creative_development.concept_developer import (
    CONCEPT_DEVELOPER_POLICY,
    ConceptDeveloperAgent,
)

memory = get_vector_store()
context_manager = ContextManager(memory)
policy_engine = PolicyEngine()


# Creative Department Agents

idea_generator = IdeaGeneratorAgent(
    memory=memory,
    context_manager=context_manager,
    policy_engine=policy_engine,
    policy=IDEA_GENERATOR_POLICY,
)

idea_critic = IdeaCriticAgent(
    memory=memory,
    context_manager=context_manager,
    policy_engine=policy_engine,
    policy=IDEA_CRITIC_POLICY,
)

concept_developer = ConceptDeveloperAgent(
    memory=memory,
    context_manager=context_manager,
    policy_engine=policy_engine,
    policy=CONCEPT_DEVELOPER_POLICY,
)

research_agent = ResearchAgent(
    memory=memory,
    context_manager=context_manager,
    policy_engine=policy_engine,
    policy=research_agent_policy,
)

# Executive Department Agents

executive_producer = ExecutiveProducerAgent(
    memory=memory,
    context_manager=context_manager,
    policy=EXECUTIVE_PRODUCER_POLICY,
    policy_engine=policy_engine,
)
