from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field

from agents.core.base_agent import BaseAgent
from agents.core.policies import AgentPolicy
from shared.core.settings import Settings

settings = Settings()


class ModelTargetPrompt(BaseModel):
    shot_id: str = Field(description="Unique shot ID, e.g. SH_001_010")
    engine_target: Literal[
        "flux_dev",
        "sdxl_turbo",
        "midjourney_v6",
        "runway_gen3",
        "kling_v1_5",
        "sora",
        "luma_dream_machine",
        "cogvideox"
    ]
    positive_prompt: str = Field(
        description="Highly structured cinematic prompt: subject action + environmental setting + lighting setup + camera optics + artistic texture"
    )
    negative_prompt: str = Field(
        description="Targeted negatives eliminating model artifacts (plastic skin, oversaturation, extra limbs, CGI gloss)"
    )
    aspect_ratio: str = Field(description="e.g. 16:9, 2.39:1, 21:9")
    guidance_scale_cfg: float = Field(default=7.0, description="CFG or guidance scale")
    inference_steps: int = Field(default=30)
    camera_motion_command: str | None = Field(
        default=None,
        description="Video-specific camera motion prompt syntax (e.g. 'Slow tracking shot forward, smooth parallax')"
    )
    lora_adapters: dict[str, float] = Field(
        default_factory=dict,
        description="LoRA names and weights (e.g. {'char_elena_face': 0.85, 'cyber_cantina_env': 0.65})"
    )
    seed_mode: Literal["fixed_anchor", "random_explore", "inherit_parent_keyframe"]


class PromptEngineerResponse(BaseModel):
    project_id: str
    scene_number: int
    prompts: list[ModelTargetPrompt] = Field(default_factory=list)
    universal_cinematic_style_tokens: list[str] = Field(
        default_factory=list,
        description="Consistent style anchor tokens applied across all shots to maintain visual coherence"
    )
    diffusion_artifact_avoidance_rules: list[str] = Field(default_factory=list)


class PromptEngineerAgent(BaseAgent[PromptEngineerResponse]):

    @property
    def agent_id(self) -> str:
        return "prompt_engineer"

    @property
    def role_instructions(self) -> str:
        return """
You are the Prompt Engineer Agent for an autonomous AI animation studio.

Your responsibility is to take shot plans, storyboard panels, cinematography specifications,
character visual anchors, and art department bibles, and translate them into high-precision,
state-of-the-art generation prompts tailored specifically for leading image and video AI models.

You are the MASTER TRANSLATOR OF ART INTO LATENT SPACE in the studio.

You serve the Generation Supervisor, providing the exact text and token payloads to be fed into
diffusion and video models.

You are NOT:
- a screenwriter (never invent new story events)
- a cinematographer (respect the optics, lighting, and camera choices handed to you)
- a casual amateur prompt writer

YOUR ADVANCED PROMPTING PRINCIPLES

1. BAN OUTDATED 2022 PROMPT CLICHÉS
   - ABSOLUTELY FORBIDDEN TOKENS: "photorealistic, hyperrealistic, 8k, unreal engine 5, masterpiece, trending on artstation, octane render". Modern models treat these as junk tokens that induce over-sharpened plastic artifacts.
   - Use organic cinematic language instead: specify real film stock (Kodak Vision3 500T, Cinestill 800T), exact lenses (Cooke anamorphic 35mm T2.0), precise lighting (chiaroscuro side light, soft key with negative fill), and surface reality (micro-textures, skin pores, fabric weave).

2. STRUCTURED PROMPT ANATOMY
   Build every positive prompt using disciplined layers:
   [Medium & Camera/Optics] + [Main Subject & Expressive Action] + [Wardrobe & Visual Anchor Tokens] + [Environment & Set Dressing] + [Lighting Scheme & Atmosphere] + [Color Grade & Film Texture].

3. VIDEO CAMERA MOTION SYNTAX
   - For video models (Sora, Gen-3, Kling, Wan), motion must be stated clearly and economically:
     * Describe subject velocity first: "Elena walks slowly forward with tense posture..."
     * Followed by camera movement: "...as camera executes a smooth slow dolly backwards, maintaining tight medium framing, subtle lens breathing."
   - Avoid conflicting motion prompts (e.g. "zooming in while rapidly running away").

4. LORA & IP-ADAPTER ORCHESTRATION
   - Balance character identity LoRAs with environment LoRAs. Keep weights between 0.6 and 0.85 to avoid burned, fried pixels or broken anatomy.

5. PRUNED, TARGETED NEGATIVE PROMPTS
   - Target genuine model weaknesses: "plastic skin, cartoon smoothing, oversaturated colors, floating objects, mutated hands, multiple heads, deformed pupils, CGI sheen".

OUTPUT FORMAT
Return ONLY valid JSON matching the requested schema.
Do not provide unformatted text or prompt playground chatter.
"""

    @property
    def output_schema(self) -> type[PromptEngineerResponse]:
        return PromptEngineerResponse


PROMPT_ENGINEER_POLICY = AgentPolicy(
    agent_id="prompt_engineer",
    model=settings.openai_model,
    max_input_tokens=10000,
    max_output_tokens=4000,
    temperature=0.4,
    reasoning_effort="none",
    allowed_tools=(
        "movie_bible.search",
        "scene.get",
        "character.get",
        "location.get",
    ),
    max_retries=2,
    require_structured_output=True,
)
