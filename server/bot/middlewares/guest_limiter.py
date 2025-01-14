from typing import Any, Callable
from aiogram import BaseMiddleware, types
from aiogram.types import Message

from bot.database.engine import session_maker
from bot.database.queries.user import get_user

class GuestLimiterMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable,
        event: Message,
        data: dict
    ) -> Any:
        if isinstance(event, types.Message):
            async with session_maker() as session:
                user = await get_user(session, event.from_user.id)
                if user and user.role == "GUEST":
                    await event.answer("Вас пока не верефицировали, подождите!")
                    return
        return await handler(event, data)
