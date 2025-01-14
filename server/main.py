from contextlib import asynccontextmanager

from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.models import init_db
import database.queries as rq


class AddTask(BaseModel):
    tg_id: int
    title: str


class CompleteTask(BaseModel):
    id: int


@asynccontextmanager
async def lifespan(app_: FastAPI):
    await init_db()
    print('Bot is ready')
    yield


app = FastAPI(title="To Do App", lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/tasks/{tg_id}")
async def tasks(tg_id: int):
    user = await rq.user.add_user(tg_id)
    return await rq.task.get_tasks(user.id)


@app.get("/api/main/{tg_id}")
async def profile(tg_id: int):
    user = await rq.user.add_user(tg_id)
    completed_tasks_count = await rq.task.get_completed_tasks_count(user.id)
    return {'completedTasks': completed_tasks_count}


@app.post("/api/add")
async def add_task(task: AddTask):
    user = await rq.user.add_user(task.tg_id)
    await rq.task.add_task(user.id, task.title)
    return {'status': 'ok'}


@app.patch("/api/completed")
async def complete_task(task: CompleteTask):
    await rq.task.update_task(task.id)
    return {'status': 'ok'}
