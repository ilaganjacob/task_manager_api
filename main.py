from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv

from contextlib import asynccontextmanager

import asyncpg
import os

load_dotenv()

db_url = os.getenv("supabase_url")


@asynccontextmanager
async def lifespan(app: FastAPI):

    app.state.db_conn = await asyncpg.connect(db_url, statement_cache_size=0)

    # assign to app.state so we share this resource across the app instance
    print("Db connected!")

    yield

    await app.state.db_conn.close()


# defines what the CLIENT sends. the SERVER defines the ID so we don't define it in here
class Task(BaseModel):
    task_desc: str
    done: bool = False


app = FastAPI(lifespan=lifespan)

tasks = []


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/tasks")
async def get_tasks():
    all_tasks = await app.state.db_conn.fetch("""
        SELECT * from tasks
""")
    return all_tasks


@app.get("/tasks/{id}")
async def get_task(id: int):
    task = await app.state.db_conn.fetchrow(
        """
    SELECT * FROM tasks WHERE id = $1
        
    """,
        id,
    )
    return task


@app.post("/tasks")
async def create_task(task: Task):
    # task is a Pydantic object, need to convert to dict
    # FastAPI parses the task into a Pydantic object -a task
    # now we need to make it into a dict, assign it a unique id, and take the "desc" and "done" from the task and finish
    # we cannot just take the task
    new_task = await app.state.db_conn.fetchrow(
        """
                                         INSERT INTO tasks(task_desc, done)
                                         VALUES($1, $2)
                                         RETURNING *
                                         """,
        task.task_desc,
        task.done,
    )
    return new_task


@app.put("/tasks/{id}")
async def update_task(id: int, task: Task):
    the_task = await app.state.db_conn.fetchrow(
        """
                                                UPDATE tasks
                                                SET task_desc=$1, done=$2
                                                WHERE ID=$3
                                                RETURNING *
                                                """,
        task.task_desc,
        task.done,
        id,
    )
    return the_task


@app.delete("/tasks/{id}")
async def delete_task(id: int):
    # This removes the task from the tasks list
    for i, task in enumerate(tasks):
        # this is the task we're searching for
        if task["id"] == id:
            tasks.pop(i)
            return {"message": "task deleted"}
    return {"message": "task not found"}
