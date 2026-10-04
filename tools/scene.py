from pydantic import BaseModel, Field
from agents.core.memory import StudioStore


class SceneGetInput(BaseModel):
    project_id: str
    scene_id: str = Field(min_length=1)


async def scene_get(store: StudioStore, input_data: SceneGetInput) -> dict | None:
    return await store.get_canon_entity(
        project_id=input_data.project_id,
        entity_id=input_data.scene_id,
        entity_type="scene",
    )
