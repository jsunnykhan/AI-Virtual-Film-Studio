from pydantic import BaseModel, Field
from agents.core.memory import StudioStore


class MovieBibleSearchInput(BaseModel):
    project_id: str
    query: str = Field(min_length=1)
    limit: int = Field(default=10, ge=1, le=50)


async def movie_bible_search(
    store: StudioStore, input_data: MovieBibleSearchInput
) -> list[dict]:
    return await store.search_canon(
        project_id=input_data.project_id,
        query=input_data.query,
        limit=input_data.limit,
    )
