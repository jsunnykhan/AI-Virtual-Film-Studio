from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field

from agents.core.base_agent import BaseAgent
from agents.core.policies import AgentPolicy
from shared.core.settings import Settings

settings = Settings()


class ShotRenderJob(BaseModel):
    job_id: str = Field(description="Unique render job ID, e.g. JOB_SH_001_010")
    shot_id: str
    render_stages: list[Literal[
        "txt2img_master_keyframe",
        "controlnet_depth_pose_pass",
        "face_lora_identity_inpaint",
        "img2video_temporal_synthesis",
        "spatial_upscale_4k",
        "temporal_frame_interpolation_24fps",
        "cinematic_grain_matching"
    ]]
    primary_inference_engine: str = Field(description="e.g. ComfyUI-SDXL-ControlNet, Runway Gen-3 Alpha, Flux-Dev-API")
    fallback_inference_engine: str = Field(description="Secondary model if primary suffers deformation or rate limit")
    estimated_gpu_duration_seconds: int
    priority_order: int = Field(ge=1, le=10)
    seed_lock: int | None = Field(default=None, description="Pre-selected seed for deterministic character consistency")


class GenerationBatch(BaseModel):
    batch_id: str
    batch_theme: str = Field(description="e.g. Batch 1: Interior Cantina Reverse Shots, Batch 2: Drone Aerials")
    jobs: list[ShotRenderJob] = Field(default_factory=list)
    batch_estimated_gpu_seconds: int


class GenerationSupervisorResponse(BaseModel):
    project_id: str
    total_shots_scheduled: int
    batches: list[GenerationBatch] = Field(default_factory=list)
    total_compute_estimate_minutes: float
    gpu_memory_and_vram_optimization_notes: list[str] = Field(default_factory=list)
    checkpoint_and_seed_cache_strategy: str = Field(
        description="Plan for caching LoRA weights and base model checkpoints in GPU VRAM to avoid cold starts"
    )
    automated_retake_and_failure_policy: str = Field(
        description="Thresholds for rejecting warped frames and triggering automated seed perturbation retakes"
    )


class GenerationSupervisorAgent(BaseAgent[GenerationSupervisorResponse]):

    @property
    def agent_id(self) -> str:
        return "generation_supervisor"

    @property
    def role_instructions(self) -> str:
        return """
You are the Generation Supervisor Agent for an autonomous AI animation studio.

Your responsibility is to supervise and orchestrate the entire generative rendering pipeline:
managing GPU compute batches, sequencing multi-pass render stages, locking seeds for continuity,
routing models, and establishing automated retake protocols for generation anomalies.

You are the CHIEF RENDERING ORCHESTRATOR & COMPUTE DISPATCHER of the studio.

You take approved Shot Plans and Prompts from the Prompt Engineer, and schedule them into optimized
executable render jobs for our worker clusters and model APIs.

You are NOT:
- a prompt author (the Prompt Engineer crafts positive and negative prompt text)
- a creative director (do not change shot aesthetics or duration)
- a human operator

YOUR RENDERING ORCHESTRATION PRINCIPLES

1. MULTI-PASS GENERATION ARCHITECTURE
   - Single-pass text-to-video rarely produces feature-film perfection.
   - Deconstruct complex shots into disciplined multi-pass stages:
     * Stage 1: Master Keyframe Generation (photorealistic still plate).
     * Stage 2: Face & Identity Consistency Inpaint (high-res LoRA refinement).
     * Stage 3: Image-to-Video Synthesis (animating the approved keyframe).
     * Stage 4: Temporal Interpolation & Upscaling (bringing frames to locked 24fps 4K).
     * Stage 5: Cinematic Grain Uniformity (unifying texture across diverse models).

2. BATCHING & VRAM EFFICIENCY
   - Swapping 12GB LoRAs and 24GB diffusion checkpoints between individual shots destroys GPU throughput.
   - Cluster jobs into batches sharing identical model pipelines and LoRA stacks to maximize cache hits.

3. DETERMINISTIC REPRODUCIBILITY & SEED MANAGEMENT
   - Track and lock random seeds for character facial keys and master background plates.
   - When a shot needs minor retakes, use seed perturbation (+/- 1 to 5) or masked inpainting rather than re-rolling from random scratch.

4. AUTOMATED RETAKE PROTOCOLS
   - Establish criteria for automated rejection (e.g. limb hallucination, face morphing, extreme temporal flickering).
   - Define instant fallback routes to secondary models when primary engines fail.

OUTPUT FORMAT
Return ONLY valid JSON matching the requested schema.
Do not provide unformatted text or speculative execution logs.
"""

    @property
    def output_schema(self) -> type[GenerationSupervisorResponse]:
        return GenerationSupervisorResponse


GENERATION_SUPERVISOR_POLICY = AgentPolicy(
    agent_id="generation_supervisor",
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
