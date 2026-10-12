from uuid import uuid4

from agents.core.states import CreativeWorkflowState
from agents.core.schemas import AgentTask

from agents.agent_container import (
    idea_generator,
    idea_critic,
    concept_developer,
    executive_producer,
    research_agent,
)

## ============================================================
# NODES
## ============================================================


async def idea_generator_node(state: CreativeWorkflowState):
    """
    Node for generating ideas.
    """
    task = AgentTask(
        task_id=state.get("task_id") or str(uuid4()),
        project_id=state.get("project_id", ""),
        agent_id="idea_generator",
        objective=(
            "Autonomously generate an original animated series or movie concept. "
            "Choose the format, genre, and story without requiring a user prompt. "
            "Use any prior producer or critic feedback to avoid repeating rejected ideas."
        ),
        input_data={
            "user_request": "Autonomously generate an original animated series or movie concept. Choose the format, genre, and story without requiring a user prompt.",
            "iteration": state.get("iteration", 0),
            "max_iterations": state.get("max_iterations", 3),
            "previous_idea": state.get("idea"),
            "executive_feedback": state.get("final_decision"),
            "critic_feedback": state.get("critique"),
        },
    )

    result = await idea_generator.run(task)
    return {
        "task_id": task.task_id,
        "iteration": state.get("iteration", 0) + 1,
        "idea": result.model_dump(),
        "status": "idea_generated" if result.success else "idea_generation_failed",
        "error": "; ".join(result.errors) if result.errors else None,
    }



async def idea_critic_node(
    state: CreativeWorkflowState,
):
    task = AgentTask(
        task_id=state.get("task_id") or str(uuid4()),
        project_id=state.get("project_id", ""),
        agent_id="idea_critic",
        objective="Evaluate the generated animated-series concept",
        input_data={
            "user_request": state.get("user_request", ""),
            "idea": state.get("idea"),
            "iteration": state.get("iteration", 0),
        },
    )

    result = await idea_critic.run(task)

    return {
        "critique": result.model_dump(),
        "status": "idea_criticized" if result.success else "idea_critic_failed",
        "error": "; ".join(result.errors) if result.errors else None,
    }


async def concept_developer_node(
    state: CreativeWorkflowState,
):
    task = AgentTask(
        task_id=state.get("task_id") or str(uuid4()),
        project_id=state.get("project_id", ""),
        agent_id="concept_developer",
        objective="Develop the approved idea into a complete series concept",
        input_data={
            "user_request": state.get("user_request", ""),
            "idea": state.get("idea"),
            "critique": state.get("critique", {}),
        },
    )

    result = await concept_developer.run(task)

    print(f"Concept Developer Result: {result.model_dump()}")

    return {
        "concept": result.model_dump(),
        "status": "concept_developed" if result.success else "concept_development_failed",
        "error": "; ".join(result.errors) if result.errors else None,
    }

async def executive_producer_node(
    state: CreativeWorkflowState,
):
    task = AgentTask(
        task_id=state.get("task_id") or str(uuid4()),
        project_id=state.get("project_id", ""),
        agent_id="executive_producer",
        objective=(
            "Review the generated creative idea for coherence and feasibility. "
            "Approve it for critic evaluation only if suitable."
        ),
        input_data={
            "user_request": state.get("user_request", ""),
            "idea": state.get("idea"),
            "critique": state.get("critique", {}),
            "concept": state.get("concept", {}),
        },
    )

    result = await executive_producer.run(task)

    return {
        "final_decision": result.model_dump(),
        "status": (
            "executive_approved"
            if result.success and result.output and result.output.approved
            else "executive_rejected"
            if result.success
            else "executive_producer_failed"
        ),
        "error": "; ".join(result.errors) if result.errors else None,
    }
    
async def research_agent_node(
    state: CreativeWorkflowState,
):
    task = AgentTask(
        task_id=state.get("task_id") or str(uuid4()),
        project_id=state.get("project_id", ""),
        agent_id="research_agent",
        objective="Conduct research to support creative development and factual accuracy.",
        input_data={
            "user_request": state.get("user_request", ""),
            "idea": state.get("idea"),
            "critique": state.get("critique", {}),
            "concept": state.get("concept", {}),
        },
    )

    result = await research_agent.run(task)

    return {
        "research_summary": result.model_dump().get("research_summary"),
        "references": result.model_dump().get("references", []),
        "status": "research_completed" if result.success else "research_failed",
        "error": "; ".join(result.errors) if result.errors else None,
    }