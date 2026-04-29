from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# defines what the CLIENT sends. the SERVER defines the ID so we don't define it in here
class Task(BaseModel):
  desc: str
  done: bool = False

tasks = [
  {"id": 1, "desc": "first", "done": False},
  {"id": 2, "desc": "second", "done": False},
]

def get_new_id():
  new_id = 1
  # loop through each task in tasks
  # at each task["id"], we can just set new_id = task["id"] + 1
  for task in tasks:
    new_id = task["id"] + 1
  return new_id



@app.get('/')
async def root():
  return {"message": "Hello World"}

@app.get('/tasks')
async def get_tasks():
  return {"tasks": tasks}

@app.get('/tasks/{id}')
async def get_task(id: int):
  for task in tasks:
    if task["id"] == id:
      return task
  return {"message": "task not found"}

@app.post("/tasks")
async def create_task(task: Task):
  # task is a Pydantic object, need to convert to dict
  # FastAPI parses the task into a Pydantic object -a task
  # now we need to make it into a dict, assign it a unique id, and take the "desc" and "done" from the task and finish
  # we cannot just take the task
  new_task = { 
    "id": get_new_id(),
    "desc": task.desc,
    "done": task.done
  }
  tasks.append(new_task)
  return new_task

@app.put('/tasks/{id}')
async def update_task(id: int, task: Task):
  for i, existing in enumerate(tasks):
    if existing["id"] == id:
        tasks[i] = {
          "id": id,
          "desc": task.desc,
          "done": task.done
        }
        return tasks[i]
  return {"message": "task not found"}

@app.delete("/tasks/{id}")
async def delete_task(id: int):
  # This removes the task from the tasks list
  for i, task in enumerate(tasks):
    # this is the task we're searching for
    if task["id"] == id:
      tasks.pop(i)
      return {"message": "task deleted"}
  return {"message": "task not found" }
