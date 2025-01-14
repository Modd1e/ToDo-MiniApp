from datetime import datetime, timedelta
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.filters import CommandStart, StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from bot.database.queries.event import get_event
from bot.database.queries.event_confirm import create_event_confirmation, get_event_confirmation, update_event_confirmation
from bot.filters.isUser import IsUser
from bot.keyboards.inline import get_callback_btns
from bot.database.queries.user import get_user, create_user
from bot.database.queries.banner import orm_get_banners, orm_get_banner_from_title
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import Bot


router = Router()
router.message.filter(IsUser())
router.message.filter(F.chat.type == "private")

class FSMConfirmation(StatesGroup):
    proof = State()


@router.callback_query(F.data.startswith("confirm_event_"))
async def confirm_event_handler(callback: CallbackQuery, session: AsyncSession, bot: Bot, state: FSMContext):
    event_id = int(callback.data.split("_")[2])
    user_tg_id = callback.from_user.id

    event = await get_event(session, event_id)
    user = await get_user(session, user_tg_id)
    confirmation = await get_event_confirmation(session, event_id, user.tg_id)

    if not event:
        await callback.answer("Событие не найдено.")
        return

    if confirmation and confirmation.confirmed:
        await callback.answer("Вы уже подтвердили это событие.")
        return


    await state.set_state(FSMConfirmation.proof)
    await state.update_data(event_id=event_id, confirmation_id = confirmation.id)
    await callback.message.answer("Отправьте подтверждение (фото, текст или фото с подписью)")


@router.message(StateFilter(FSMConfirmation.proof))
async def process_proof(message: Message, state: FSMContext, session: AsyncSession, bot: Bot):
    confirmation_id = (await state.get_data())['confirmation_id']
    if not message.photo and not message.text:
        await message.answer("Пожалуйста, отправьте фото или текст сs подписью.")
        return
    
    if message.photo:
        proof_msg = message.caption
        proof_img = message.photo[-1].file_id
        await update_event_confirmation(
            session,
            confirmation_id=confirmation_id,
            data={
                "proof_msg": proof_msg,
                "proof_img": proof_img,
            }
        )
    elif message.text:
        proof = message.text
        await update_event_confirmation(
            session,
            confirmation_id=confirmation_id,
            data={
                "proof_msg": proof
            }
        )
    else:
        await message.answer("Пожалуйста, отправьте фото или текст с подписью.")
        return

    # proof_msg = message.id
    # data = await state.get_data()
    # event_id = data['event_id']
    # user_id = message.from_user.id

    # user = await get_user(session, user_id)
    # confirmation = await get_event_confirmation(session, event_id, user.id)
    # if not confirmation:
    #     confirmation = await create_event_confirmation(session, event_id, user.id)
    
    # await update_event_confirmation(session, confirmation.id, {"proof_msg": proof_msg})
    
    await message.answer("Доказательство отправлено на рассмотрение.")
    await state.clear()
