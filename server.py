from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os

import models

models.init_db()

app = FastAPI(title="Todo API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")


class TodoCreate(BaseModel):
    title: str
    category: str = "Family"


class TodoUpdate(BaseModel):
    title: str | None = None
    completed: bool | None = None


@app.get("/")
def index():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


@app.get("/api/todos")
def list_todos(category: str | None = Query(None)):
    return models.get_todos(category)


@app.post("/api/todos", status_code=201)
def create_todo(body: TodoCreate):
    return models.add_todo(body.title, body.category)


@app.put("/api/todos/{todo_id}")
def update_todo(todo_id: int, body: TodoUpdate):
    if body.title is not None:
        result = models.update_todo(todo_id, body.title)
    else:
        result = models.toggle_todo(todo_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return result


@app.delete("/api/todos/{todo_id}")
def delete_todo(todo_id: int):
    if not models.delete_todo(todo_id):
        raise HTTPException(status_code=404, detail="Todo not found")
    return {"ok": True}
