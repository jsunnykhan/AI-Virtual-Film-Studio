# AI Movie Studio

## Repository Structure

```text
ai-movie-studio/
├── apps/
│   ├── studio-api/
│   ├── studio-web/
│   └── worker-api/
├── agents/
│   ├── core/
│   │   ├── base_agent.py
│   │   ├── context.py
│   │   ├── memory.py
│   │   ├── schemas.py
│   │   └── policies.py
│   ├── executive/
│   ├── story/
│   ├── directing/
│   ├── production_design/
│   ├── vfx/
│   ├── audio/
│   ├── generation/
│   ├── postproduction/
│   └── quality/
├── workflows/
│   ├── movie_workflow.py
│   ├── story_workflow.py
│   ├── production_workflow.py
│   └── postproduction_workflow.py
├── orchestration/
│   ├── temporal/
│   ├── kafka/
│   └── scheduler/
├── model_gateway/
│   ├── litellm/
│   ├── router/
│   ├── budgets/
│   ├── cache/
│   └── providers/
├── context_engine/
│   ├── retriever.py
│   ├── composer.py
│   ├── summarizer.py
│   ├── token_counter.py
│   └── budget_manager.py
├── memory/
│   ├── postgres/
│   ├── pgvector/
│   └── redis/
├── media/
│   ├── image/
│   ├── video/
│   ├── audio/
│   ├── vfx/
│   └── editing/
├── gpu/
│   ├── scheduler/
│   ├── workers/
│   ├── vastai/
│   └── health/
├── qc/
│   ├── visual/
│   ├── audio/
│   ├── continuity/
│   └── technical/
├── shared/
│   ├── events/
│   ├── contracts/
│   └── enums/
├── infra/
│   ├── docker/
│   ├── kafka/
│   ├── postgres/
│   ├── redis/
│   ├── minio/
│   └── temporal/
└── docs/
    ├── architecture/
    ├── agents/
    ├── workflows/
    └── movie-bible/
```

## Agent Hierarchy

```text
L0 STUDIO ORCHESTRATOR
│
├── L1 EXECUTIVE PRODUCER
│   ├── Production Manager
│   ├── Budget Agent
│   └── Compute Optimizer
│
├── L1 CREATIVE DIRECTOR / SHOWRUNNER
│   ├── L2 STORY DEPARTMENT
│   │   ├── Research
│   │   ├── Concept
│   │   ├── Story Architect
│   │   ├── Worldbuilding
│   │   ├── Character
│   │   ├── Screenwriter
│   │   ├── Dialogue
│   │   └── Script Editor
│   │
│   ├── L2 DIRECTOR DEPARTMENT
│   │   ├── Director
│   │   ├── Storyboard
│   │   ├── Cinematography
│   │   └── Shot Planner
│   │
│   ├── L2 PRODUCTION DESIGN
│   │   ├── Environment
│   │   ├── Costume
│   │   └── Props
│   │
│   ├── L2 VFX
│   │   ├── VFX Supervisor
│   │   └── VFX Planner
│   │
│   └── L2 AUDIO
│       ├── Casting
│       ├── Voice Director
│       ├── Voice Generator
│       ├── Music Supervisor
│       ├── Composer
│       └── Sound Designer
│
├── L1 PRODUCTION ENGINE
│   ├── Prompt Engineer
│   ├── Model Router
│   ├── Image Generator
│   ├── Video Generator
│   ├── Audio Generator
│   └── Asset Generator
│
├── L1 POST PRODUCTION
│   ├── Editor
│   ├── VFX Compositor
│   ├── Colorist
│   ├── Sound Editor
│   ├── Mixer
│   └── Localization
│
├── L1 QUALITY
│   ├── Film Critic
│   ├── Continuity Agent
│   ├── Technical QC
│   └── Rights / Safety
│
└── L1 DISTRIBUTION
    ├── Trailer
    ├── Marketing
    └── Distribution
```
