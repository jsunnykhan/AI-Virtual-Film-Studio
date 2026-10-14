from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field

from agents.core.base_agent import BaseAgent
from agents.core.policies import AgentPolicy
from shared.core.settings import Settings

settings = Settings()


class IntellectualPropertyRiskFlag(BaseModel):
    flag_id: str = Field(description="Unique flag ID, e.g. IP_FLAG_001_LOGO")
    risk_category: Literal[
        "trademark_brand_infringement",
        "copyrighted_character_clone",
        "celebrity_likeness_misappropriation",
        "copyrighted_music_melody_overlap",
        "proprietary_architectural_design"
    ]
    severity: Literal["blocking_legal_liability", "moderate_clearance_required", "low_fair_use_arguable", "safe_incidental"]
    affected_scene_or_shot_id: str
    infringement_description: str = Field(
        description="Exact element flagged (e.g. 'Hero prop resembles Apple iPhone logo and casing', 'Antagonist face closely mimics Keanu Reeves')"
    )
    corrective_cleanse_instructions: str = Field(
        description="Instructions for Prompt Engineer or VFX Compositor to remove or alter the element to ensure safe public release"
    )


class ContentSafetyRatingAssessment(BaseModel):
    mpaa_rating_equivalent: Literal["G", "PG", "PG-13", "R", "NC-17"]
    tv_parental_guidelines_rating: Literal["TV-Y", "TV-G", "TV-PG", "TV-14", "TV-MA"]
    violence_and_gore_index: int = Field(ge=1, le=10)
    language_profanity_index: int = Field(ge=1, le=10)
    sensual_and_mature_themes_index: int = Field(ge=1, le=10)
    content_descriptor_tags: list[str] = Field(
        default_factory=list,
        description="e.g. ['Intense Sci-Fi Violence', 'Brief Strong Language', 'Thematic Horror Elements']"
    )


class TechnicalDeliveryComplianceCheck(BaseModel):
    standard_name: str = Field(description="e.g. ITU-R BS.1770-4 Loudness, SMPTE ST 2067-21 IMF, EBU R128")
    status: Literal["compliant", "non_compliant_requires_reencode", "waiver_granted"]
    diagnostic_details: str


class RightsDeliveryResponse(BaseModel):
    project_id: str
    clearance_report_id: str
    final_clearance_verdict: Literal[
        "cleared_for_worldwide_distribution",
        "blocked_due_to_critical_ip_liability",
        "conditional_approval_pending_cleanses"
    ]
    clearance_summary: str
    ip_risk_flags: list[IntellectualPropertyRiskFlag] = Field(default_factory=list)
    content_rating: ContentSafetyRatingAssessment
    technical_compliance_checks: list[TechnicalDeliveryComplianceCheck] = Field(default_factory=list)
    provenance_and_licensing_audit: str = Field(
        description="Verification that all reference images, voice models, and music training weights possess verifiable commercial rights"
    )


class RightsDeliveryReviewerAgent(BaseAgent[RightsDeliveryResponse]):

    @property
    def agent_id(self) -> str:
        return "rights_delivery_reviewer"

    @property
    def role_instructions(self) -> str:
        return """
You are the Rights & Delivery Reviewer Agent (Chief Legal Counsel & Content Safety Officer) for an autonomous AI animation studio.

Your responsibility is to conduct an uncompromising audit of the final film project across intellectual
property, copyright, trademark, right of publicity (celebrity likeness), content safety ratings, and
technical delivery standards before commercial distribution.

You are the FINAL LEGAL & COMPLIANCE SHIELD of the studio.

You audit all production artifacts prior to distributor packaging or public broadcasting.

You are NOT:
- a creative reviewer (you do not judge plot quality; you protect the studio from lawsuits and platform bans)
- an executive producer (you provide binding clearance assessments and remedial instructions)
- a casual reviewer

YOUR COMPLIANCE & LEGAL AUDIT PRINCIPLES

1. CELEBRITY LIKENESS & RIGHT OF PUBLICITY
   - Generative diffusion models often overfit on famous faces.
   - Inspect character faces with forensic scrutiny: If a character's face, hair, and posture inadvertently mimic a recognizable living actor, celebrity, or public figure without a likeness contract, immediately flag as BLOCKING LEGAL LIABILITY.
   - Demand facial perturbation or inpainting to ensure fictional uniqueness.

2. TRADEMARK & BRAND INFRINGEMENT
   - Scan environments, vehicles, props, and costumes for commercial logos, trade dress, or protected designs (e.g. Nike swoosh, Apple logo, Ferrari body lines, Coca-Cola script).
   - Require immediate removal or fictional rebranding (e.g. replace with an approved in-universe fictional corporation).

3. COPYRIGHT & FRANCHISE DERIVATION
   - Guard against accidental copying of protected franchise elements: Lightsabers, Starfleet insignias, Bat-symbols, Pokéballs, or verbatim iconic dialogue ("May the Force be with you").
   - Ensure the story does not plagiarize copyrighted plots or unique expressive works.

4. CONTENT RATING & PLATFORM COMPLIANCE
   - Evaluate violence, gore, nudity, language, and terror against MPAA and TV Parental Guidelines.
   - Flag any scene that inadvertently pushes a PG-13 project into an unintended R rating.

5. PROVENANCE & TECHNICAL COMPLIANCE
   - Verify that all voice models, music prompts, and asset references comply with ethical AI provenance and licensing rules.
   - Confirm export formats comply with distribution specifications.

OUTPUT FORMAT
Return ONLY valid JSON matching the requested schema.
Do not provide speculative legalese essays or conversational preamble.
"""

    @property
    def output_schema(self) -> type[RightsDeliveryResponse]:
        return RightsDeliveryResponse


RIGHTS_DELIVERY_REVIEWER_POLICY = AgentPolicy(
    agent_id="rights_delivery_reviewer",
    model=settings.openai_model,
    max_input_tokens=10000,
    max_output_tokens=4000,
    temperature=0.2,
    reasoning_effort="none",
    allowed_tools=(
        "movie_bible.search",
        "scene.get",
        "character.get",
    ),
    max_retries=2,
    require_structured_output=True,
)
