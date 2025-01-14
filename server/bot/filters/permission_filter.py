from aiogram.filters import Filter
from aiogram import Bot, types
from bot.database.queries.role import get_role_by_name
from bot.database.queries.user import get_user
from bot.database.engine import session_maker
import logging

class PermissionFilter(Filter):
    def __init__(self, permission: str | list) -> None:
        self.permission = permission

    async def __call__(self, message: types.Message, bot: Bot) -> bool:
        async with session_maker() as session:
            user = await get_user(session, message.from_user.id)
            if not user:
                await message.answer("Пользователь не найден в базе данных.")
                logging.error(f"User with tg_id {message.from_user.id} not found.")
                return False

            role = await get_role_by_name(session, user.role)
            if not role:
                await message.answer("Роль пользователя не найдена в базе данных.")
                logging.error(f"Role '{user.role}' not found for user with tg_id {message.from_user.id}.")
                return False

            logging.info(f"User '{user.game_username}' with role '{user.role}' attempting access. Permissions: {self.permission}")
            logging.info(f"Role '{role.name}' permissions: {role}")

            if isinstance(self.permission, str):
                if getattr(role, self.permission, False):
                    return True
            elif isinstance(self.permission, list):
                for perm in self.permission:
                    if getattr(role, perm, False):
                        return True

            await message.answer("У вас немає доступу до цієї функції! Будьласка зверніця до адміністратора.")
            logging.warning(f"Access denied for user '{user.game_username}' with role '{user.role}' for permissions: {self.permission}")
            return False
