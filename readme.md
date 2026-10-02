ai-movie-studio/
│
├── apps/
│   ├── studio-api/
│   ├── studio-web/
│   └── worker-api/
│
├── agents/
│   ├── core/
│   │   ├── base_agent.py
│   │   ├── context.py
│   │   ├── memory.py
│   │   ├── schemas.py
│   │   └── policies.py
│   │
│   ├── executive/
│   ├── story/
│   ├── directing/
│   ├── production_design/
│   ├── vfx/
│   ├── audio/
│   ├── generation/
│   ├── postproduction/
│   └── quality/
│
├── workflows/
│   ├── movie_workflow.py
│   ├── story_workflow.py
│   ├── production_workflow.py
│   └── postproduction_workflow.py
│
├── orchestration/
│   ├── temporal/
│   ├── kafka/
│   └── scheduler/
│
├── model_gateway/
│   ├── litellm/
│   ├── router/
│   ├── budgets/
│   ├── cache/
│   └── providers/
│
├── context_engine/
│   ├── retriever.py
│   ├── composer.py
│   ├── summarizer.py
│   ├── token_counter.py
│   └── budget_manager.py
│
├── memory/
│   ├── postgres/
│   ├── pgvector/
│   └── redis/
│
├── media/
│   ├── image/
│   ├── video/
│   ├── audio/
│   ├── vfx/
│   └── editing/
│
├── gpu/
│   ├── scheduler/
│   ├── workers/
│   ├── vastai/
│   └── health/
│
├── qc/
│   ├── visual/
│   ├── audio/
│   ├── continuity/
│   └── technical/
│
├── shared/
│   ├── events/
│   ├── contracts/
│   └── enums/
│
├── infra/
│   ├── docker/
│   ├── kafka/
│   ├── postgres/
│   ├── redis/
│   ├── minio/
│   └── temporal/
│
└── docs/
    ├── architecture/
    ├── agents/
    ├── workflows/
    └── movie-bible/