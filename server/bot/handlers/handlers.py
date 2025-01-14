import re
from sqlalchemy.ext.asyncio import AsyncSession

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from bot.filters.isUser import IsUser
from bot.keyboards.inline import get_callback_btns

from bot.database.queries.debt import create_debt
from bot.database.queries.role import get_role_by_name
from bot.database.queries.user import create_user, get_user
from bot.database.queries.banner import orm_get_banner_from_title

router = Router()
router.message.filter(IsUser())
router.message.filter(F.chat.type == "private")

back_btn = get_callback_btns(btns={"Назад": "main_menu"})
class FSM_change_profile(StatesGroup):
    game_username = State()


async def main_menu_btns(role):
    kb = {}
    size = ()
    kb["Профиль 👤"] = "profile_menu"
    kb["События 🗓️"] = "events_menu_"
    size += (2, )
    
    if (
        role.can_change_role or 
        role.can_ban_and_unban_users or 
        role.can_spam or 
        role.can_manage_debts or 
        role.can_confirm_guests or 
        role.can_spam or 
        role.can_sync_db
    ):
        kb["Админ меню ⚙️"] = "admin_menu"
        size += (1, )

    kb["О нас ℹ️"] = "about"
    kb["Тех-поддержка 🛠️"] = "tech_support"
    size += (2, )

    return get_callback_btns(btns=kb, sizes=size)


@router.message(Command("menu"))
async def main_menu_cmd(message: Message, session: AsyncSession):
    user = await get_user(session, message.from_user.id)
    role = await get_role_by_name(session, user.role)
    
    kb = await main_menu_btns(role)
    banner = await orm_get_banner_from_title(session, "Main")
    
    await message.answer_photo(
        photo=banner.image,
        caption=banner.description.format(first_name = user.game_username),
        reply_markup=kb
    )


@router.callback_query(F.data == "main_menu")
async def main_menu_callback(callback: CallbackQuery, session: AsyncSession):
    user = await get_user(session, callback.from_user.id)
    role = await get_role_by_name(session, user.role)
    
    kb = await main_menu_btns(role)
    banner = await orm_get_banner_from_title(session, "Main")
    
    await callback.answer(banner.callback_answer)
    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=banner.image,
            caption=banner.description.format(first_name = user.game_username)
        ),
        reply_markup=kb
    )


@router.callback_query(F.data == "about")
async def main_menu(callback: CallbackQuery, session: AsyncSession):
    banner = await orm_get_banner_from_title(session, "About")

    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=banner.image,
            caption=banner.description
        ),
        reply_markup=back_btn
    )


@router.callback_query(F.data == "profile_menu")
async def profile(callback: CallbackQuery, session: AsyncSession):
    user = await get_user(session, callback.from_user.id)
    role = await get_role_by_name(session, user.role)
    banner = await orm_get_banner_from_title(session, "Profile")
    await callback.answer(banner.callback_answer)
    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=banner.image,
            caption=(
                f"ℹ️ Ваша анкета\n\n"
                f" 👤 Ник в аве: <b>{user.game_username}</b>\n"
                f" 👑 Должность: <b>{role.title}</b>\n"
                f" 👑 Долг: <b>PASS</b>\n"
            )
        ),
        reply_markup=get_callback_btns(
            btns={
                "📝 Изменить ник": "change_profile",
                "📝 Спистать долги": "change_my_debt",
                "◀ Назад": "main_menu"
            },
            sizes=(1, 1)
        )
    )


@router.callback_query(F.data == "change_profile")
async def profile(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    user = await get_user(session, callback.from_user.id)
    await callback.answer(" ")
    await callback.message.answer(
        text=(
            f"Введи свой ник в Аватарии:!\n"
        )
    )
    await state.set_state(FSM_change_profile.game_username)


@router.message(FSM_change_profile.game_username)
async def get_game_username(message: Message, state: FSMContext, session: AsyncSession):
    if re.fullmatch(r"^[a-zA-Zа-яА-ЯёЁїЇіІєЄґҐ0-9_]+$", message.text):
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
        await main_menu_cmd(message, session)
        await state.clear()
    else:
        await message.answer("nickname_error")
        await state.set_state(FSM_change_profile.game_username)


@router.callback_query(F.data == "tech_support")
async def profile(callback: CallbackQuery, session: AsyncSession):
    banner = await orm_get_banner_from_title(session, "Tech support")
    await callback.answer(banner.callback_answer)
    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=banner.image,
            caption=banner.description
        ),
        reply_markup=back_btn
    )


@router.callback_query(F.data == "change_my_debt")
async def profile(callback: CallbackQuery, session: AsyncSession):
    banner = await orm_get_banner_from_title(session, "change_my_debt")
    await callback.answer(banner.callback_answer)
    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=banner.image,
            caption=banner.description
        ),
        reply_markup=get_callback_btns(
            btns={
                "◀ Назад": "profile_menu"
            },
            sizes=(1,)
        )
    )
