from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Any, Awaitable, Callable
from pydantic import BaseModel


class ToolName(str, Enum):
    MOVIE_BIBLE_SEARCH = "movie_bible.search"
    CHARACTER_GET = "character.get"
    LOCATION_GET = "location.get"
    SCENE_GET = "scene.get"
    SHOT_CREATE = "shot.create"

    def __str__(self) -> str:
        return self.value


Tools = ToolName

__all__ = ["ToolName", "Tools", "ToolSpec"]


@dataclass(frozen=True)
class ToolSpec:
    name: str | ToolName
    description: str
    input_model: type[BaseModel]
    handler: Callable[..., Awaitable[Any]]

