from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field

from agents.core.base_agent import BaseAgent
from agents.core.policies import AgentPolicy
from shared.core.settings import Settings

settings = Settings()


class Milestone(BaseModel):
    name: str = Field(description="Milestone name, e.g. Script Freeze, Pre-Viz Complete, Final Render")
    phase: str = Field(description="Development, Pre-Production, Production, Post-Production, Delivery")
    target_timeline: str = Field(description="Estimated timing or sequence order")
    dependencies: list[str] = Field(default_factory=list, description="Milestones that must finish before this begins")
    deliverables: list[str] = Field(default_factory=list, description="Artifacts delivered upon milestone completion")


class SceneSchedule(BaseModel):
    scene_id: str = Field(description="Scene identifier")
    complexity_rating: Literal["low", "medium", "high", "extreme"] = Field(description="Estimated generation complexity")
    gpu_render_tier: Literal["standard", "high_priority", "burst"] = Field(description="Compute allocation tier")
    dependency_assets: list[str] = Field(default_factory=list, description="Characters, sets, props needed before scene begins")
    priority: int = Field(ge=1, le=10, description="10 is highest priority for rendering order")
    contingency_buffer_percent: int = Field(default=20, description="Buffer for regeneration / retries")


class ResourceAllocation(BaseModel):
    department: str = Field(description="Department name")
    token_budget_ratio: float = Field(ge=0.0, le=1.0, description="Proportion of total LLM token budget")
    gpu_compute_allocation_hours: float = Field(description="Estimated GPU hours for this department/phase")
    storage_mb_allocation: int = Field(description="Storage space allocated for outputs")
    optimization_recommendations: list[str] = Field(default_factory=list)


class AssetDependency(BaseModel):
    asset_id: str = Field(description="Character, environment, or prop identifier")
    asset_type: Literal["character", "environment", "prop", "voice_model", "music_stem"]
    required_by_scenes: list[str] = Field(default_factory=list)
    lead_time_phase: str = Field(description="Phase in which this asset must be locked")


class ProductionPlanResponse(BaseModel):
    plan_id: str
    project_id: str
    target_runtime_minutes: float = Field(
        description="The exact runtime duration in minutes decided autonomously by the AI agents (e.g. 5, 20, 90, 120, 200+ minutes). Never hardcoded."
    )
    production_strategy_summary: str
    milestones: list[Milestone] = Field(default_factory=list)
    scene_schedule_breakdown: list[SceneSchedule] = Field(default_factory=list)
    resource_allocations: list[ResourceAllocation] = Field(default_factory=list)
    critical_path: list[str] = Field(default_factory=list, description="Sequence of dependent tasks determining project completion")
    asset_dependency_matrix: list[AssetDependency] = Field(default_factory=list)
    risk_mitigation_plan: list[str] = Field(default_factory=list)
    production_readiness_verdict: Literal["approved_for_prep", "needs_budget_revision", "blocked_on_resources"]


class ProductionManagerAgent(BaseAgent[ProductionPlanResponse]):

    @property
    def agent_id(self) -> str:
        return "production_manager"

    @property
    def role_instructions(self) -> str:
        return """
You are the Production Manager Agent for an autonomous AI animation studio.

Your responsibility is to turn the Executive Producer's production brief into an executable,
resource-optimized, dependency-aware production plan that guides every department from
script development to final delivery.

You are the CHIEF OPERATIONAL ARCHITECT of the studio.

You work immediately after the Executive Producer has approved a project brief, and you coordinate
operational milestones across Story, Directing, Art, Audio, Generation, and Post-Production.

You are NOT:
- an executive producer (you do not decide what project gets greenlit)
- a creative screenwriter (you do not write screenplay pages)
- a director (you do not choose aesthetic shots)
- an artist or prompt writer

YOUR CORE OBJECTIVES

1. SCHEDULE & MILESTONES
   - Establish realistic phase progressions: Story/Script -> Art/Design -> Directing/Pre-viz ->
     Audio Tracking -> Generation/Rendering -> Post-Production -> Quality/Delivery.
   - Define hard dependency locks (e.g., Script Freeze must precede Shot Planning; Character Model Lock
     must precede Shot Generation).

2. COMPUTE & RESOURCE ALLOCATION
   - Treat GPU compute, inference tokens, and render retries as finite, precious assets.
   - Allocate GPU compute tiers according to scene visual complexity (e.g. low-complexity dialogue
     twoshots receive standard tier; high-velocity multi-character action receives burst/high priority).
   - Reserve a strict retry buffer (minimum 15-25%) for generation failures and quality retakes.

3. ASSET DEPENDENCY TRACKING
   - Map out Day-Out-of-Days (DOOD) asset dependencies.
   - Flag shared assets (recurring characters, master environments, hero props) and schedule their
     creation first so downstream scenes never block on missing character reference loras or master plates.

4. CRITICAL PATH & BOTTLENECK ANALYSIS
   - Identify the single longest chain of dependent events that dictates total delivery time.
   - Provide concrete risk mitigations for potential pipeline bottlenecks (e.g., fallback prompt strategies,
     batching shots by location, reusing lighting setups).

5. OPERATIONAL FEASIBILITY & AUTONOMOUS RUNTIME DECISION
   - You autonomously decide the project runtime duration (`target_runtime_minutes`).
   - Do NOT use hardcoded durations. The story may call for a 5-minute showcase, a 20-minute episode, a 90-minute feature, or an epic 200-minute cinematic saga.
   - Match the runtime to narrative depth, character count, and scope decided with the Executive Producer.
   - Break this runtime into a concrete scene-by-scene schedule breakdown.

HANDOFF REQUIREMENTS

Provide actionable constraints to:
- Story Architect & Screenwriter: target runtime minutes, scene count, character limits per scene, pacing bounds.
- Director & Cinematographer: maximum shot counts, reusable set requirements.
- Generation Supervisor: batch sizes, render prioritization, GPU budget ceilings.
- Quality Delivery Reviewer: technical milestone checkpoints.

OUTPUT FORMAT

Return ONLY valid JSON matching the requested schema.
Do not include conversational filler, speculative musings, or markdown outside the JSON payload.
Do not invent unverified infrastructure resources.
"""

    @property
    def output_schema(self) -> type[ProductionPlanResponse]:
        return ProductionPlanResponse


PRODUCTION_MANAGER_POLICY = AgentPolicy(
    agent_id="production_manager",
    model=settings.openai_model,
    max_input_tokens=10000,
    max_output_tokens=4000,
    temperature=0.3,
    reasoning_effort="none",
    allowed_tools=(
        "movie_bible.search",
        "scene.get",
    ),
    max_retries=2,
    require_structured_output=True,
)
