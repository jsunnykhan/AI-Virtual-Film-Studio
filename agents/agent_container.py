from __future__ import annotations

from typing import Any

from agents.core.context import ContextManager
from agents.core.policies import PolicyEngine
from memory.vector_store import get_vector_store

# Executive Department
from agents.executive_department.executive_producer import (
    ExecutiveProducerAgent,
    EXECUTIVE_PRODUCER_POLICY,
)
from agents.executive_department.production_manager import (
    ProductionManagerAgent,
    PRODUCTION_MANAGER_POLICY,
)

# Creative Development Department
from agents.creative_development.idea_generator import (
    IdeaGeneratorAgent,
    IDEA_GENERATOR_POLICY,
)
from agents.creative_development.idea_critic import (
    IdeaCriticAgent,
    IDEA_CRITIC_POLICY,
)
from agents.creative_development.concept_developer import (
    ConceptDeveloperAgent,
    CONCEPT_DEVELOPER_POLICY,
)
from agents.creative_development.research_agent import (
    ResearchAgent,
    research_agent_policy,
)

# Story & Screenwriting Department
from agents.story_screenwriting_department.story_architect import (
    StoryArchitectAgent,
    STORY_ARCHITECT_POLICY,
)
from agents.story_screenwriting_department.world_designer import (
    WorldDesignerAgent,
    WORLD_DESIGNER_POLICY,
)
from agents.story_screenwriting_department.character_designer import (
    CharacterDesignerAgent,
    CHARACTER_DESIGNER_POLICY,
)
from agents.story_screenwriting_department.screenwriter import (
    ScreenwriterAgent,
    SCREENWRITER_POLICY,
)
from agents.story_screenwriting_department.script_editor import (
    ScriptEditorAgent,
    SCRIPT_EDITOR_POLICY,
)

# Directing Department
from agents.directing_department.director import (
    DirectorAgent,
    DIRECTOR_POLICY,
)
from agents.directing_department.cinematographer import (
    CinematographerAgent,
    CINEMATOGRAPHER_POLICY,
)
from agents.directing_department.storyboard_artist import (
    StoryboardArtistAgent,
    STORYBOARD_ARTIST_POLICY,
)
from agents.directing_department.shot_planner import (
    ShotPlannerAgent,
    SHOT_PLANNER_POLICY,
)

# Production Design Department
from agents.production_design_department.production_designer import (
    ProductionDesignerAgent,
    PRODUCTION_DESIGNER_POLICY,
)

# Audio Department
from agents.audio_department.voice_director import (
    VoiceDirectorAgent,
    VOICE_DIRECTOR_POLICY,
)
from agents.audio_department.music_sound_designer import (
    MusicSoundDesignerAgent,
    MUSIC_SOUND_DESIGNER_POLICY,
)

# Generation Department
from agents.generation_department.prompt_engineer import (
    PromptEngineerAgent,
    PROMPT_ENGINEER_POLICY,
)
from agents.generation_department.generation_supervisor import (
    GenerationSupervisorAgent,
    GENERATION_SUPERVISOR_POLICY,
)

# Post-Production Department
from agents.postproduction_department.editor import (
    EditorAgent,
    EDITOR_POLICY,
)
from agents.postproduction_department.finishing_supervisor import (
    FinishingSupervisorAgent,
    FINISHING_SUPERVISOR_POLICY,
)

# Quality & Delivery Department
from agents.quality_delivery_department.continuity_qc import (
    ContinuityQCAgent,
    CONTINUITY_QC_POLICY,
)
from agents.quality_delivery_department.rights_delivery_reviewer import (
    RightsDeliveryReviewerAgent,
    RIGHTS_DELIVERY_REVIEWER_POLICY,
)


memory = get_vector_store()
context_manager = ContextManager(memory)
policy_engine = PolicyEngine()


# ============================================================
# EXECUTIVE DEPARTMENT
# ============================================================

executive_producer = ExecutiveProducerAgent(
    memory=memory,
    context_manager=context_manager,
    policy=EXECUTIVE_PRODUCER_POLICY,
    policy_engine=policy_engine,
)

production_manager = ProductionManagerAgent(
    memory=memory,
    context_manager=context_manager,
    policy=PRODUCTION_MANAGER_POLICY,
    policy_engine=policy_engine,
)


# ============================================================
# CREATIVE DEVELOPMENT DEPARTMENT
# ============================================================

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

research_agent = ResearchAgent(
    memory=memory,
    context_manager=context_manager,
    policy=research_agent_policy,
    policy_engine=policy_engine,
)


# ============================================================
# STORY & SCREENWRITING DEPARTMENT
# ============================================================

story_architect = StoryArchitectAgent(
    memory=memory,
    context_manager=context_manager,
    policy=STORY_ARCHITECT_POLICY,
    policy_engine=policy_engine,
)

world_designer = WorldDesignerAgent(
    memory=memory,
    context_manager=context_manager,
    policy=WORLD_DESIGNER_POLICY,
    policy_engine=policy_engine,
)

character_designer = CharacterDesignerAgent(
    memory=memory,
    context_manager=context_manager,
    policy=CHARACTER_DESIGNER_POLICY,
    policy_engine=policy_engine,
)

screenwriter = ScreenwriterAgent(
    memory=memory,
    context_manager=context_manager,
    policy=SCREENWRITER_POLICY,
    policy_engine=policy_engine,
)

script_editor = ScriptEditorAgent(
    memory=memory,
    context_manager=context_manager,
    policy=SCRIPT_EDITOR_POLICY,
    policy_engine=policy_engine,
)


# ============================================================
# DIRECTING DEPARTMENT
# ============================================================

director = DirectorAgent(
    memory=memory,
    context_manager=context_manager,
    policy=DIRECTOR_POLICY,
    policy_engine=policy_engine,
)

cinematographer = CinematographerAgent(
    memory=memory,
    context_manager=context_manager,
    policy=CINEMATOGRAPHER_POLICY,
    policy_engine=policy_engine,
)

storyboard_artist = StoryboardArtistAgent(
    memory=memory,
    context_manager=context_manager,
    policy=STORYBOARD_ARTIST_POLICY,
    policy_engine=policy_engine,
)

shot_planner = ShotPlannerAgent(
    memory=memory,
    context_manager=context_manager,
    policy=SHOT_PLANNER_POLICY,
    policy_engine=policy_engine,
)


# ============================================================
# PRODUCTION DESIGN DEPARTMENT
# ============================================================

production_designer = ProductionDesignerAgent(
    memory=memory,
    context_manager=context_manager,
    policy=PRODUCTION_DESIGNER_POLICY,
    policy_engine=policy_engine,
)


# ============================================================
# AUDIO DEPARTMENT
# ============================================================

voice_director = VoiceDirectorAgent(
    memory=memory,
    context_manager=context_manager,
    policy=VOICE_DIRECTOR_POLICY,
    policy_engine=policy_engine,
)

music_sound_designer = MusicSoundDesignerAgent(
    memory=memory,
    context_manager=context_manager,
    policy=MUSIC_SOUND_DESIGNER_POLICY,
    policy_engine=policy_engine,
)


# ============================================================
# GENERATION DEPARTMENT
# ============================================================

prompt_engineer = PromptEngineerAgent(
    memory=memory,
    context_manager=context_manager,
    policy=PROMPT_ENGINEER_POLICY,
    policy_engine=policy_engine,
)

generation_supervisor = GenerationSupervisorAgent(
    memory=memory,
    context_manager=context_manager,
    policy=GENERATION_SUPERVISOR_POLICY,
    policy_engine=policy_engine,
)


# ============================================================
# POST-PRODUCTION DEPARTMENT
# ============================================================

editor = EditorAgent(
    memory=memory,
    context_manager=context_manager,
    policy=EDITOR_POLICY,
    policy_engine=policy_engine,
)

finishing_supervisor = FinishingSupervisorAgent(
    memory=memory,
    context_manager=context_manager,
    policy=FINISHING_SUPERVISOR_POLICY,
    policy_engine=policy_engine,
)


# ============================================================
# QUALITY & DELIVERY DEPARTMENT
# ============================================================

continuity_qc = ContinuityQCAgent(
    memory=memory,
    context_manager=context_manager,
    policy=CONTINUITY_QC_POLICY,
    policy_engine=policy_engine,
)

rights_delivery_reviewer = RightsDeliveryReviewerAgent(
    memory=memory,
    context_manager=context_manager,
    policy=RIGHTS_DELIVERY_REVIEWER_POLICY,
    policy_engine=policy_engine,
)


# ============================================================
# STUDIO AGENT REGISTRY
# ============================================================

AGENT_REGISTRY: dict[str, Any] = {
    # Executive
    "executive_producer": executive_producer,
    "production_manager": production_manager,
    # Creative Development
    "idea_generator": idea_generator,
    "idea_critic": idea_critic,
    "concept_developer": concept_developer,
    "research_agent": research_agent,
    # Story & Screenwriting
    "story_architect": story_architect,
    "world_designer": world_designer,
    "character_designer": character_designer,
    "screenwriter": screenwriter,
    "script_editor": script_editor,
    # Directing
    "director": director,
    "cinematographer": cinematographer,
    "storyboard_artist": storyboard_artist,
    "shot_planner": shot_planner,
    # Production Design
    "production_designer": production_designer,
    # Audio
    "voice_director": voice_director,
    "music_sound_designer": music_sound_designer,
    # Generation
    "prompt_engineer": prompt_engineer,
    "generation_supervisor": generation_supervisor,
    # Post-Production
    "editor": editor,
    "finishing_supervisor": finishing_supervisor,
    # Quality & Delivery
    "continuity_qc": continuity_qc,
    "rights_delivery_reviewer": rights_delivery_reviewer,
}


def get_agent(agent_id: str) -> Any:
    """Retrieve an instantiated studio agent by its unique agent_id."""
    if agent_id not in AGENT_REGISTRY:
        raise KeyError(f"Agent '{agent_id}' not found in AGENT_REGISTRY. Available agents: {list(AGENT_REGISTRY.keys())}")
    return AGENT_REGISTRY[agent_id]
