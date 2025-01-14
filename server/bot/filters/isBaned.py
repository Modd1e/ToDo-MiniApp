from aiogram.filters import Filter
from aiogram import Bot, types
from bot.database.queries.user import get_user
from bot.database.engine import session_maker


class IsBaned(Filter):
    async def __call__(self, message: types.Message, bot: Bot) -> bool:
        async with session_maker() as session:
            user = await get_user(session, message.from_user.id)
            if user:
                if user.is_baned == True:
                    await message.answer("Вы забанены!\n\nОбратитесь к <a href=”https://t.me/mamosos”>@mamosos</a>")
                    return False
            else:
                return False
        return
