from pydantic import BaseModel, Field
from agents.core.memory import StudioStore


class LocationGetInput(BaseModel):
    project_id: str
    location_id: str = Field(min_length=1)


async def location_get(store: StudioStore, input_data: LocationGetInput) -> dict | None:
    return await store.get_canon_entity(
        project_id=input_data.project_id,
        entity_id=input_data.location_id,
        entity_type="location",
    )
