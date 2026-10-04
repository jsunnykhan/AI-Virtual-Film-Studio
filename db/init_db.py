import asyncio
import logging
from db.connection import get_asyncpg_dsn, get_pool
from shared.core.settings import get_settings

logger = logging.getLogger(__name__)


async def init_db() -> None:
    """Initialize Postgres database tables, pgvector extension, and vector indexes."""
    settings = get_settings()
    dim = settings.embedding_dim

    pool = await get_pool()

    async with pool.acquire() as conn:
        logger.info("Initializing Postgres Vector DB schema...")
        
        # Ensure pgvector extension
        await conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")

        # Projects table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                project_id VARCHAR(255) PRIMARY KEY,
                name VARCHAR(255),
                summary TEXT,
                metadata JSONB DEFAULT '{}'::jsonb,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            );
        """)

        # Canon entities table with vector embedding
        await conn.execute(f"""
            CREATE TABLE IF NOT EXISTS canon_entities (
                id BIGSERIAL PRIMARY KEY,
                project_id VARCHAR(255) NOT NULL,
                entity_id VARCHAR(255) NOT NULL,
                entity_type VARCHAR(100) NOT NULL,
                data JSONB NOT NULL,
                embedding vector({dim}),
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW(),
                CONSTRAINT uq_canon_project_entity UNIQUE (project_id, entity_id)
            );
        """)

        # Indexes for fast retrieval and vector similarity search
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_canon_proj_type 
            ON canon_entities (project_id, entity_type);
        """)

        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_canon_embedding 
            ON canon_entities USING hnsw (embedding vector_cosine_ops);
        """)

        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_canon_data_gin 
            ON canon_entities USING gin (data);
        """)

        # Agent runs history table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS agent_runs (
                id BIGSERIAL PRIMARY KEY,
                project_id VARCHAR(255) NOT NULL,
                agent_id VARCHAR(100) NOT NULL,
                task_id VARCHAR(255) NOT NULL,
                result JSONB NOT NULL,
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
        """)

        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_agent_runs_proj_agent 
            ON agent_runs (project_id, agent_id, created_at DESC);
        """)

        # Tasks table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                task_id VARCHAR(255) PRIMARY KEY,
                project_id VARCHAR(255),
                agent_id VARCHAR(100),
                objective TEXT,
                status VARCHAR(50) DEFAULT 'pending',
                data JSONB NOT NULL,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            );
        """)

        logger.info("Postgres Vector DB schema initialization completed successfully.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(init_db())
