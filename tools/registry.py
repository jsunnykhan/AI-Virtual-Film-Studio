from __future__ import annotations
from typing import Any

from agents.core.memory import StudioStore
from tools.base import ToolSpec
from tools.character import CharacterGetInput, character_get
from tools.location import LocationGetInput, location_get
from tools.movie_bible import MovieBibleSearchInput, movie_bible_search
from tools.scene import SceneGetInput, scene_get
from tools.shot import ShotCreateInput, shot_create


class ToolRegistry:
    def __init__(self, store: StudioStore, tools: list[ToolSpec]) -> None:
        self.store = store
        self._tools = {tool.name: tool for tool in tools}

    def get(self, name: str) -> ToolSpec | None:
        return self._tools.get(name)

    def names(self) -> tuple[str, ...]:
        return tuple(self._tools.keys())

    def schemas(self) -> list[dict[str, Any]]:
        return [
            {
                "name": spec.name,
                "description": spec.description,
                "input_schema": spec.input_model.model_json_schema(),
            }
            for spec in self._tools.values()
        ]

    async def execute(self, name: str, arguments: dict[str, Any]) -> Any:
        spec = self.get(name)
        if spec is None:
            raise KeyError(f"Unknown tool: {name}")
        validated = spec.input_model.model_validate(arguments)
        return await spec.handler(self.store, validated)


def build_registry(store: StudioStore) -> ToolRegistry:
    return ToolRegistry(
        store=store,
        tools=[
            ToolSpec(
                "movie_bible.search",
                "Search approved Movie Bible/canon records for a project.",
                MovieBibleSearchInput,
                movie_bible_search,
            ),
            ToolSpec(
                "character.get",
                "Get one canonical character by ID.",
                CharacterGetInput,
                character_get,
            ),
            ToolSpec(
                "location.get",
                "Get one canonical location by ID.",
                LocationGetInput,
                location_get,
            ),
            ToolSpec(
                "scene.get",
                "Get one canonical scene by ID.",
                SceneGetInput,
                scene_get,
            ),
            ToolSpec(
                "shot.create",
                "Create a new planned shot artifact in project canon.",
                ShotCreateInput,
                shot_create,
            ),
        ],
    )
