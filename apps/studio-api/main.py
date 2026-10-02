from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def read_root():
    return {"abc": 1}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}
