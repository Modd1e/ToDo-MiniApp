from fastapi import APIRouter
from fastapi.requests import Request

from app.crud import user

router = APIRouter(
    prefix="/user",
    tags=["User"]
)

@router.get("/")
async def check(tg_id=None):
    
    if tg_id:

        user.read(tg_id)
    return {"data": "server worked"}
