from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Awaitable, Callable
from pydantic import BaseModel


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    input_model: type[BaseModel]
    handler: Callable[..., Awaitable[Any]]

