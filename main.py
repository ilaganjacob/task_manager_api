from fastapi import FastAPI

app = FastAPI()
tasks = [
  {"id": 1, "desc": "first"},
  {"id": 2, "desc": "second"},
]


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
async def create_task(task):
  return