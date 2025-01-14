import logging

from datetime import datetime
from aiogram import F, Router, types
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, InputMediaVideo
from aiogram.filters import Command, StateFilter, or_f
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.methods.send_message import SendMessage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State


from bot.database.models import User
from bot.database.queries.event_confirm import get_event_confirmation_by_id, update_event_confirmation, get_event_confirmation
from bot.database.queries.role import get_role_by_name
from bot.database.queries.user import get_user
from bot.filters.isUser import IsUser
from bot.utils.sheets_sync import sync_data
from bot.filters.isAdmin import IsAdmin
from bot.keyboards.inline import get_callback_btns
from bot.database.queries.banner import orm_get_banner_from_title as get_banner
from bot.database.engine import drop_db
from bot.database.engine import session_maker
from bot.filters.permission_filter import PermissionFilter
from main import bot

router = Router()
router.message.filter(IsUser())
router.message.filter(F.chat.type == "private")


async def admin_menu_btns(role):
    kb = {}
    if role.can_change_role or role.can_ban_and_unban_users or role.can_spam:
        kb["Список пользователей 👥"] = "users_page_"
    if role.can_confirm_events:
        kb["Подтверждение событий 👥"] = "event_confirm_menu_"
    # if role.can_manage_debts:
    #     kb["Управление долгами 💰"] = "manage_debts"
    if role.can_confirm_guests:
        kb["Верификация гостей 🚪"] = "guest_menu_"
    # if role.can_spam:
    #     kb["Разослать сообщения 📨"] = "send_message"
    if role.can_sync_db:
        kb["Синхронизировать БД 🔄"] = "sync_db"

    kb["Назад"] = "main_menu"

    return get_callback_btns(btns=kb, sizes=(1,))


@router.callback_query(F.data == "admin_menu")
async def admin_manu(callback: CallbackQuery, session: AsyncSession):
    user = await get_user(session, callback.from_user.id)
    role = await get_role_by_name(session, user.role)
    banner = await get_banner(session, "admin_menu")
    await callback.answer(banner.callback_answer)
    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=banner.image,
            caption=banner.description
        ),
        reply_markup=await admin_menu_btns(role)
    )


@router.callback_query(PermissionFilter("can_sync_db"), F.data == "sync_db")
async def sync_db(callback: CallbackQuery):
    await callback.answer("Подождите, синхронизация базы данных...")
    processing_message = await callback.message.answer("Синхронизация базы данных, пожалуйста, подождите...")

    try:
        await sync_data()
        await processing_message.edit_text(
            text="Успех! База данных успешно синхронизирована.",
            reply_markup=get_callback_btns(
                btns={
                    "Назад": "admin_menu"
                },
                sizes=(1,)
            )
        )
    except Exception as e:
        await processing_message.edit_text("Что-то пошло не так при синхронизации.")
        logging.error(f"Ошибка при синхронизации базы данных: {e}")











# async def send_message_to_all(bot, message_id, session: AsyncSession):
#     # Запрос к базе данных для получения списка tg_id
#     users = await session.execute(select(User.tg_id))
#     user_ids = [user[0] for user in users.all()]

#     original_message = await bot.get_message(message.chat.id, message_id)

#     if original_message.photo:
#         media = InputMediaPhoto(original_message.photo[-1].file_id)
#     elif original_message.video:
#         media = InputMediaVideo(original_message.video.file_id)
#     else:
#         media = original_message.text

#     # Отправка сообщений всем пользователям
#     for user_id in user_ids:
#         try:
#             await bot.send_media(user_id, media)
#         except Exception as e:
#             print(f"Ошибка при отправке сообщения пользователю {user_id}: {e}")


# @router.callback_query(PermissionFilter("can_spam"), F.data == "send_message_confirm")
# async def handle_confirmation(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
#     data = await state.get_data()
#     message_id = data.get("message_id")

#     await send_message_to_all(bot, message_id, session)

#     await callback.message.answer("Сообщение отправлено.")
#     await state.clear()


# @router.callback_query(F.data.startswith("approve_confirmation_"))
# async def approve_confirmation_handler(callback: CallbackQuery, session: AsyncSession):
#     confirmation_id = int(callback.data.split("_")[2])

#     async with session_maker() as session:
#         confirmation = await get_event_confirmation_by_id(session, confirmation_id) # Функцию нужно создать

#         if not confirmation:
#             await callback.answer("Подтверждение не найдено.")
#             return

#         await update_event_confirmation(session, confirmation.id, {"confirmed": True, "confirmation_time": datetime.now()})

#     await callback.answer("Подтверждение одобрено.")
#     # ... (обновить сообщение или отправить уведомление пользователю)


# # Вам нужно создать хендлер, который будет показывать админу
# # список неподтвержденных событий с кнопками для подтверждения
# # и функцию get_event_confirmation_by_id
