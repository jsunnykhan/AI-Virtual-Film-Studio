from pydantic import BaseModel, Field
from agents.core.memory import StudioStore


class CharacterGetInput(BaseModel):
    project_id: str
    character_id: str = Field(min_length=1)


async def character_get(
    store: StudioStore, input_data: CharacterGetInput
) -> dict | None:
    return await store.get_canon_entity(
        project_id=input_data.project_id,
        entity_id=input_data.character_id,
        entity_type="character",
    )
