from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any, cast

from fastapi import FastAPI
from pydantic import BaseModel

from db.connection import close_pool
from db.init_db import init_db
from shared.core.tracing import configure_tracing
from workflows.creative_workflow import build_creative_workflow


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    configure_tracing()
    await init_db()
    yield
    await close_pool()


app = FastAPI(lifespan=lifespan)


class Item(BaseModel):
    project_id: str = "demo"
    workflow_id: str = "creative-demo"
    task_id: str = "task-001"
    user_request: str = "Create a fun animated series about a lost robot."
    iteration: int = 0
    max_iterations: int = 3


@app.post("/")
async def read_root(item: Item):
    workflow = build_creative_workflow()
    return await workflow.ainvoke(
        cast(Any, item.model_dump()),
        config={"recursion_limit": 20},
    )


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}
