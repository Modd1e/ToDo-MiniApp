import re

from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.filters import CommandStart, StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from bot.database.queries.debt import create_debt
from bot.filters.isUser import IsUser
from bot.handlers.guest_confirm import new_guest
from bot.keyboards.inline import get_callback_btns
from bot.handlers.handlers import main_menu_cmd
from bot.database.queries.user import get_user, create_user
from bot.database.queries.banner import orm_get_banners, orm_get_banner_from_title

router = Router()
router.message.filter(F.chat.type == "private")

game_username_regex = r'^[a-zA-Zа-яА-ЯёЁїЇіІєЄґҐ0-9_]+$'

class FSM_registration(StatesGroup):
    game_username = State()


@router.message(CommandStart())
async def start(message: Message, session: AsyncSession, state: FSMContext):
    user = await get_user(session, message.from_user.id)
    if user:
        await main_menu_cmd(message, session)
    else:
        await message.answer(
            text=(
                f"Добро пожаловать в клуб! \n"
                f"Введи свой ник в Аватарии мне, чтобы я смог тебя зарегистрировать:"
            )
        )
        await state.set_state(FSM_registration.game_username)


@router.message(FSM_registration.game_username)
async def get_game_username(message: Message, state: FSMContext, session: AsyncSession):
    if re.fullmatch(game_username_regex, message.text):
        user = await create_user(
            session,
            data={
                "tg_id": message.from_user.id,
                "username": message.from_user.username,
                "firstname": message.from_user.first_name,
                "lastname": message.from_user.last_name,
                "game_username": message.text,
                "role": "GUEST"
            }
        )
        await create_debt(
            session,
            data={
                "user_id": user.tg_id,
                "amount": 0
            }
        )
        await message.answer("Подождите, лидер или помощник проверяет, состоите ли вы в клубе в Аватарии.")
        await new_guest(session)
        await state.clear()
    else:
        await message.answer("nickname_error")
        await state.set_state(FSM_registration.game_username)


# @router.message()
# async def any_message(message: Message, session: AsyncSession):
#     user = await get_user(session, message.from_user.id)
#     if user:
#         if user.role == "GUEST":
#             await message.answer("Вас пока не верефицировали, подождите!")
