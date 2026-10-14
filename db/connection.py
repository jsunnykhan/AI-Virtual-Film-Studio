import asyncio
from typing import Optional
import asyncpg
from pgvector.asyncpg import register_vector

from shared.core.settings import get_settings

_pool: Optional[asyncpg.Pool] = None
_pool_lock = asyncio.Lock()


def get_asyncpg_dsn(url: str | None = None) -> str:
    """Normalize SQLAlchemy or standard PostgreSQL connection strings for asyncpg."""
    if url is None:
        url = get_settings().database_url

    if url.startswith("postgresql+asyncpg://"):
        return "postgresql://" + url[len("postgresql+asyncpg://"):]
    if url.startswith("postgresql+psycopg://"):
        return "postgresql://" + url[len("postgresql+psycopg://"):]
    return url


async def _init_connection(conn: asyncpg.Connection) -> None:
    """Register pgvector type on every pooled connection."""
    await register_vector(conn)


async def get_pool() -> asyncpg.Pool:
    """Get or create the global asyncpg connection pool."""
    global _pool
    if _pool is not None and not _pool._closed:
        return _pool

    async with _pool_lock:
        if _pool is not None and not _pool._closed:
            return _pool

        dsn = get_asyncpg_dsn()
        
        # Ensure database is reachable with retry loop (essential for docker-compose startup)
        direct_conn = None
        max_retries = 20
        for attempt in range(1, max_retries + 1):
            try:
                direct_conn = await asyncpg.connect(dsn)
                break
            except Exception as exc:
                if attempt == max_retries:
                    raise RuntimeError(f"Could not connect to PostgreSQL after {max_retries} attempts: {exc}") from exc
                await asyncio.sleep(2)

        if direct_conn:
            try:
                await direct_conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            finally:
                await direct_conn.close()

        _pool = await asyncpg.create_pool(
            dsn=dsn,
            min_size=2,
            max_size=15,
            init=_init_connection,
        )
        return _pool


async def close_pool() -> None:
    """Close the global connection pool."""
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None
