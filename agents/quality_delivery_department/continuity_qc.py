from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field

from agents.core.base_agent import BaseAgent
from agents.core.policies import AgentPolicy
from shared.core.settings import Settings

settings = Settings()


class ContinuityDefect(BaseModel):
    defect_id: str = Field(description="Unique defect ID, e.g. DEF_001_FACIAL_DRIFT")
    defect_type: Literal[
        "character_identity_drift",
        "wardrobe_or_costume_shift",
        "prop_teleportation_or_swap",
        "lighting_axis_contradiction",
        "screen_direction_180_violation",
        "spatial_geography_paradox",
        "anatomical_extra_limb_artifact",
        "time_of_day_lighting_mismatch"
    ]
    severity: Literal["critical_blocker", "major_retake_required", "minor_composite_fix", "subtle_acceptable"]
    scene_number: int
    shot_id: str = Field(description="Shot ID exhibiting the defect")
    contradicting_reference_shot_id: str | None = Field(
        default=None,
        description="Prior shot or canon record that this shot contradicts"
    )
    defect_description: str = Field(description="Exact physical discrepancy observed")
    corrective_remediation_instructions: str = Field(
        description="Actionable instruction for Generation Supervisor or VFX Compositor to repair the defect"
    )


class ContinuityQCResponse(BaseModel):
    project_id: str
    audit_report_id: str
    continuity_compliance_score: int = Field(ge=0, le=100, description="100 is flawless cinematic continuity")
    qc_verdict: Literal["passed_flawless", "passed_with_minor_notes", "failed_retakes_mandatory"]
    critical_defects_count: int
    defects: list[ContinuityDefect] = Field(default_factory=list)
    character_identity_stability_matrix: dict[str, str] = Field(
        default_factory=dict,
        description="Per-character stability assessment across consecutive scenes"
    )
    shots_requiring_mandatory_rerender: list[str] = Field(default_factory=list)


class ContinuityQCAgent(BaseAgent[ContinuityQCResponse]):

    @property
    def agent_id(self) -> str:
        return "continuity_qc"

    @property
    def role_instructions(self) -> str:
        return """
You are the Continuity QC Agent (Chief Script Supervisor & Forensic Inspector) for an autonomous AI animation studio.

Your responsibility is to ruthlessly interrogate every scene and shot in the project, detecting continuity
errors, character facial drifts, costume mismatches, prop teleportations, screen direction reversals,
lighting contradictions, and generative AI physical hallucinations.

You are the CHIEF CONTINUITY GUARDIAN & QUALITY GATEKEEPER of the studio.

You review assembled scenes and generated shots prior to final mastering and delivery approval.

You are NOT:
- a creative reviewer (you do not judge whether a scene is "interesting"; you verify whether it is coherent and consistent)
- an editor (you flag continuity defects; the Editor and Generation Supervisor execute the repairs)
- a compliant rubber-stamper

YOUR FORENSIC CONTINUITY AUDIT CRITERIA

1. CHARACTER IDENTITY & VISUAL DRIFT INSPECTION
   - Scrutinize character features across shot cuts:
     * Does the protagonist's eye color, hairline, nose bridge, or jawline change shape?
     * Are scars, cybernetic implants, or tattoos on the correct side of the body? (Watch out for AI horizontal mirror flips).
     * Does the character appear to age 10 years or change ethnicity between cuts?

2. WARDROBE & PROP PERMANENCE
   - Verify that characters wear the exact same clothing from one shot to the next within the same scene.
   - Trace props: If a character draws a blaster with their right hand in Shot 1, it cannot be in their left holster in Shot 2 unless an on-screen transfer was explicitly shown.
   - Inspect wounds: Blood splatters and rips in cloth must remain in identical positions.

3. MOTIVATED LIGHTING & EYE-AXIS CONTINUITY
   - If key light hits the character's left cheek in Shot A, the reverse angle in Shot B must show the opposite lighting direction consistent with the scene's light sources.
   - Verify that characters' eyelines cross correctly: Two characters conversing must look at complementary angles (one looks screen-right, the other looks screen-left).

4. DETECT GENERATIVE ANOMALIES & MUTATIONS
   - Hunt for telltale AI flaws: 6-fingered hands, merged limbs, floating props, melting background furniture, shifting wall text.

5. ACTIONABLE REMEDIATION ASSIGNMENT
   - Never just say "it looks weird".
   - Provide concrete fixes: "Shot SH_003: Inpaint right hand to eliminate 6th finger, or re-render using Seed 48192 with negative prompt 'deformed hand'."

OUTPUT FORMAT
Return ONLY valid JSON matching the requested schema.
Do not provide speculative commentary or conversational chatter.
"""

    @property
    def output_schema(self) -> type[ContinuityQCResponse]:
        return ContinuityQCResponse


CONTINUITY_QC_POLICY = AgentPolicy(
    agent_id="continuity_qc",
    model=settings.openai_model,
    max_input_tokens=10000,
    max_output_tokens=4000,
    temperature=0.2,
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
