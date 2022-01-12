from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


items = {}


class Item(BaseModel):
    id: int


@app.get("/items")
def list_items():
    return list(items.values())


@app.post("/items", status_code=201)
def create_item(body: Item):
    items[body.id] = body
    return body


@app.get("/items/{id}")
def get_item(id: int):
    return Item(items[id])
