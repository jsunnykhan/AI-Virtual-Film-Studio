from agents.executive_department.executive_producer import (
    EXECUTIVE_PRODUCER_POLICY,
    ExecutiveProducerAgent,
)
from memory.vector_store import get_vector_store
from agents.core.context import ContextManager
from agents.core.policies import PolicyEngine

memory = get_vector_store()
context_manager = ContextManager(memory)
policy_engine = PolicyEngine()


# Executive Department Agents

executive_producer = ExecutiveProducerAgent(
    memory=memory,
    context_manager=context_manager,
    policy=EXECUTIVE_PRODUCER_POLICY,
    policy_engine=policy_engine,
)
