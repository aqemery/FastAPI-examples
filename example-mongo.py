from pymongo import MongoClient, ASCENDING
from bson.objectid import ObjectId
from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel

db = MongoClient().db
db.books.create_index([("id", ASCENDING)], unique=True)
db.books.create_index([("title", ASCENDING)], unique=True)

app = FastAPI()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_, exc):
    return PlainTextResponse(str(exc), status_code=400)


class Book(BaseModel):
    id: str = None
    title: str
    author: str
    score: float
    ratings: int
    checked_out: bool


@app.get("/books")
def list_books(skip: int = 0, limit: int = 10):
    return [Book(**b) for b in db.books.find(skip=skip, limit=limit)]


@app.post("/books", status_code=201)
def create_books(book: Book):
    new_book = book.dict()
    new_book["id"] = str(ObjectId())
    db.books.insert_one(new_book)
    return Book(**new_book)


@app.get("/books/{id}")
def get_book(id: str):
    query = db.books.find_one({"id": id})
    if not query:
        raise HTTPException(status_code=404, detail="Error: Book not found")
    return Book(**query)


@app.put("/books/{id}")
def update_book(id: str, book: Book):
    replaced = db.books.find_one_and_replace({"id": id}, book.dict())
    if not replaced:
        raise HTTPException(status_code=404, detail="Error: Book not found")
    return Book(**book)


@app.delete("/books/{id}")
def update_book(id: str):
    deleted = db.books.find_one_and_delete({"id": id})
    if not deleted:
        raise HTTPException(status_code=404, detail="Error: Book not found")


@app.post("/books/{id}:checkout")
def update_book(id: str):
    update = db.books.find_one_and_update(
        {"id": id, "checked_out": False}, {"$set": {"checked_out": True}}
    )
    if not update:
        raise HTTPException(
            status_code=404, detail="Error: Book not found or already checked out"
        )
