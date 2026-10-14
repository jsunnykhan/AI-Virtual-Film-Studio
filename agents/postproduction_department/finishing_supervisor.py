from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field

from agents.core.base_agent import BaseAgent
from agents.core.policies import AgentPolicy
from shared.core.settings import Settings

settings = Settings()


class ColorDecisionListShot(BaseModel):
    shot_id: str = Field(description="Unique shot ID, e.g. SH_001_010")
    scene_number: int
    target_color_space: Literal["ACEScct", "Rec709", "DCI_P3", "Rec2020_HDR"]
    slope_rgb: list[float] = Field(default=[1.0, 1.0, 1.0], description="RGB multiplier (highlights/gain)")
    offset_rgb: list[float] = Field(default=[0.0, 0.0, 0.0], description="RGB offset (shadows/lift)")
    power_rgb: list[float] = Field(default=[1.0, 1.0, 1.0], description="RGB exponent (midtones/gamma)")
    saturation: float = Field(default=1.0, description="Overall chroma saturation multiplier")
    lut_emulation_profile: str = Field(description="e.g. Kodak 2383 Print Film, Arri LogC to 709 Warm Tone")
    skin_tone_protection_protocol: str = Field(
        description="Vectorscope skin-tone line verification and isolation to prevent radioactive or grey faces"
    )


class VFXCompositingPass(BaseModel):
    shot_id: str
    ai_artifact_cleanup_instructions: list[str] = Field(
        default_factory=list,
        description="Micro-rotoscoping extra fingers, smoothing warped background lines, edge defringing"
    )
    optical_effects_to_composite: list[str] = Field(
        default_factory=list,
        description="Anamorphic lens flares, atmospheric smoke particles, muzzle flashes, volumetric dust passes"
    )
    motion_blur_matching: str = Field(description="Synthetic 180-degree shutter motion blur matching camera speed")


class AudioMasteringSpec(BaseModel):
    target_delivery_standard: Literal["ebu_r128_minus_23_lufs", "streaming_minus_14_lufs", "theatrical_minus_27_lufs"]
    integrated_loudness_target_lufs: float
    true_peak_ceiling_dbfs: float = Field(default=-1.0, description="Maximum allowable peak to prevent inter-sample clipping")
    loudness_range_lra: float = Field(description="Dynamic range spread in LU")
    multiband_compression_and_limiting: str


class FinishingSupervisorResponse(BaseModel):
    project_id: str
    master_conform_id: str
    aces_pipeline_configuration: str
    color_grading_manifest: list[ColorDecisionListShot] = Field(default_factory=list)
    vfx_compositing_passes: list[VFXCompositingPass] = Field(default_factory=list)
    audio_mastering_conform: AudioMasteringSpec
    grain_and_texture_unification: str = Field(
        description="Organic 35mm film grain overlay profile applied across all shots to bond diverse model outputs"
    )
    delivery_codec_and_container: str = Field(
        description="e.g. Apple ProRes 4444 XQ, 3840x2160, 24.000 fps, 12-bit 4:4:4, Linear PCM 24-bit 48kHz"
    )
    finishing_verdict: Literal["approved_for_delivery_qc", "regrade_required", "vfx_defringe_required"]


class FinishingSupervisorAgent(BaseAgent[FinishingSupervisorResponse]):

    @property
    def agent_id(self) -> str:
        return "finishing_supervisor"

    @property
    def role_instructions(self) -> str:
        return """
You are the Finishing Supervisor Agent for an autonomous AI animation studio.

Your responsibility is to oversee the final technical and artistic finishing of the film:
authoring ASC CDL color grading parameters, supervising VFX compositing and defringing passes,
unifying disparate generative AI textures under a cohesive organic film grain, and mastering
audio loudness to broadcast and theatrical standards.

You are the MASTER OF CONFORM, COLOR & MASTERS in the studio.

You take picture-locked edits from the Editor, Cinematography guidelines, and Audio mixes,
and produce the final master finishing specification.

You are NOT:
- an editor (you conform the locked cut, you do not rearrange scenes)
- a cinematographer (you realize the DP's lighting intentions through digital color science)
- a sound composer

YOUR FINISHING PRINCIPLES

1. ACES COLOR WORKFLOW & ASC CDL CONTROL
   - Operate in scene-linear ACES color space.
   - Author precise ASC CDL (Slope, Offset, Power, Saturation) values for each shot to ensure seamless contrast and color transitions across shot cuts.
   - Strictly protect the Skin Tone line on the vectorscope. Never allow human characters to take on the green or magenta shifts common in AI video renders.

2. ELIMINATE "MODEL JARRING" VIA GRAIN UNIFICATION
   - Different AI video models render with subtly different micro-textures and compression artifacts.
   - Apply a mathematically calibrated organic film stock grain pass (e.g. 35mm 500T Kodak stock emulation) across the entire film to bind disparate generation sources into a unified photographic medium.

3. CLEANUP & DEFRINGING
   - Detect AI edge fringe artifacts (halo borders around animated subjects) and author corrective matte feathering and edge blur instructions.
   - Composite volumetric haze, particles, or lighting flares to conceal generative boundary edges.

4. AUDIO LOUDNESS RIGOR (ITU-R BS.1770 / EBU R128)
   - Ensure final audio adheres strictly to target delivery loudness standards (e.g. -14 LUFS for web/streaming, -23/-24 LUFS for broadcast).
   - Enforce a true-peak ceiling of -1.0 dBFS to prevent digital distortion across lossy streaming codecs.

OUTPUT FORMAT
Return ONLY valid JSON matching the requested schema.
Do not provide unformatted text or speculative post-production essays.
"""

    @property
    def output_schema(self) -> type[FinishingSupervisorResponse]:
        return FinishingSupervisorResponse


FINISHING_SUPERVISOR_POLICY = AgentPolicy(
    agent_id="finishing_supervisor",
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
