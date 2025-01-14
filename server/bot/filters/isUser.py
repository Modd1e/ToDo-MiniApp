from aiogram.filters import Filter
from aiogram import Bot, types
from bot.database.queries.user import get_user
from bot.database.engine import session_maker


class IsUser(Filter):
    async def __call__(self, message: types.Message, bot: Bot) -> bool:
        async with session_maker() as session:
            user = await get_user(session, message.from_user.id)
            if user:
                if user.role != "GUEST":
                    return True
            else:
                return False
