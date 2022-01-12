from fastapi import FastAPI

app = FastAPI()

items = []


@app.get("/items")
def list_items():
    return items


@app.post("/items", status_code=201)
def create_item(body: int):
    items.append(body)
    return body
