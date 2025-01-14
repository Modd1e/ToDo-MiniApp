from aiogram.filters import Filter
from aiogram import Bot, types
from bot.database.queries.user import get_user
from bot.database.engine import session_maker


class IsAdmin(Filter):
    async def __call__(self, message: types.Message, bot: Bot) -> bool:
        async with session_maker() as session:
            user = await get_user(session, message.from_user.id)
            if not user:
                return False
            return user.role in {"4", "3"}
