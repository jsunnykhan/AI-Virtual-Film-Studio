from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any, cast

from fastapi import FastAPI
from pydantic import BaseModel

from db.connection import close_pool
from db.init_db import init_db
from shared.core.tracing import configure_tracing
from workflows.creative_workflow import build_creative_workflow
import uuid


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    configure_tracing()
    await init_db()
    yield
    await close_pool()


app = FastAPI(lifespan=lifespan)


class Item(BaseModel):
    project_id: str
    iteration: int
    max_iterations: int


@app.post("/")
async def read_root():
    item_dict = {
        "project_id": str(uuid.uuid4()),
        "iteration": 0,
        "max_iterations": 3
    }
    item_dict["status"] = "started"
    item_dict["project_id"] = item_dict.get("project_id", str(uuid.uuid4()))

    workflow = build_creative_workflow()
    return await workflow.ainvoke(
        cast(Any, item_dict),
        config={"recursion_limit": 20},
    )


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}
