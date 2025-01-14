from sqlalchemy import select, update, delete, func
from server.database.models import async_session, Task
from pydantic import BaseModel, ConfigDict


class TaskSchema(BaseModel):
    id: int
    title: str
    completed: bool
    user: int
    
    model_config = ConfigDict(from_attributes=True)


async def get_tasks(user_id):
    async with async_session() as session:
        tasks = await session.scalars(
            select(Task).where(Task.user == user_id, Task.completed == False)
        )
        
        serialized_tasks = [
            TaskSchema.model_validate(t).model_dump() for t in tasks
        ]
        
        return serialized_tasks


async def get_completed_tasks_count(user_id):
    async with async_session() as session:
        return await session.scalar(select(func.count(Task.id)).where(Task.completed == True))


async def add_task(user_id, title):
    async with async_session() as session:
        new_task = Task(
            title=title,
            user=user_id
        )
        session.add(new_task)
        await session.commit()


async def update_task(task_id):
    async with async_session() as session:
        await session.execute(update(Task).where(Task.id == task_id).values(completed=True))
        await session.commit()
