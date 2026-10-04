from pydantic import BaseModel, Field, field_validator
from agents.core.memory import StudioStore


class ShotCreateInput(BaseModel):
    project_id: str
    shot_id: str = Field(min_length=1)
    scene_id: str = Field(min_length=1)
    duration_sec: float = Field(gt=0, le=60)
    characters: list[str] = Field(default_factory=list)
    location_id: str | None = None
    action: str = Field(min_length=1)
    camera: dict = Field(default_factory=dict)
    lighting: str | None = None
    reference_assets: list[str] = Field(default_factory=list)
    generation_model: str | None = None
    generation_workflow: str | None = None
    negative_constraints: list[str] = Field(default_factory=list)
    expected_output: str = "video"

    @field_validator("project_id", "shot_id", "scene_id", "action")
    @classmethod
    def not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Value must not be blank.")
        return value


async def shot_create(store: StudioStore, input_data: ShotCreateInput) -> dict:
    existing = await store.get_canon_entity(
        project_id=input_data.project_id,
        entity_id=input_data.shot_id,
        entity_type="shot",
    )
    if existing is not None:
        raise ValueError(
            f"Shot '{input_data.shot_id}' already exists. "
            "Create a new version/ID instead of overwriting it."
        )

    data = {
        "shot_id": input_data.shot_id,
        "scene_id": input_data.scene_id,
        "duration_sec": input_data.duration_sec,
        "characters": input_data.characters,
        "location_id": input_data.location_id,
        "action": input_data.action,
        "camera": input_data.camera,
        "lighting": input_data.lighting,
        "reference_assets": input_data.reference_assets,
        "generation_model": input_data.generation_model,
        "generation_workflow": input_data.generation_workflow,
        "negative_constraints": input_data.negative_constraints,
        "expected_output": input_data.expected_output,
        "generation_status": "planned",
        "version": 1,
    }

    return await store.upsert_canon(
        project_id=input_data.project_id,
        entity_id=input_data.shot_id,
        entity_type="shot",
        data=data,
    )
