from fastapi import APIRouter
from fastapi.requests import Request
from aiogram.types import Update

import main

router = APIRouter(
    prefix="/webhook",
    tags=["WebHook"]
)


@router.post("/telegram")
async def webhook(request: Request):
    update = Update.model_validate(await request.json(), context={"bot": main.bot})
    await main.dp.feed_update(main.bot, update)
