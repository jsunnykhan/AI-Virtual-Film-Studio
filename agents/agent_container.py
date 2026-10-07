from memory.vector_store import get_vector_store
from agents.core.context import ContextManager
from agents.core.policies import PolicyEngine
from agents.creative.idea_generator import IDEA_GENERATOR_POLICY, IdeaGeneratorAgent
from agents.creative.idea_critic import IDEA_CRITIC_POLICY, IdeaCriticAgent
from agents.creative.concept_developer import CONCEPT_DEVELOPER_POLICY, ConceptDeveloperAgent

memory = get_vector_store()
context_manager = ContextManager(memory)
policy_engine = PolicyEngine()


idea_generator = IdeaGeneratorAgent(
    memory=memory,
    context_manager=context_manager,
    policy=IDEA_GENERATOR_POLICY,
    policy_engine=policy_engine,
)


idea_critic = IdeaCriticAgent(
    memory=memory,
    context_manager=context_manager,
    policy=IDEA_CRITIC_POLICY,
    policy_engine=policy_engine,
)

concept_developer = ConceptDeveloperAgent(
    memory=memory,
    context_manager=context_manager,
    policy=CONCEPT_DEVELOPER_POLICY,
    policy_engine=policy_engine,
)
