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

from bot.database.queries.debt import get_debt, update_debt
from bot.database.queries.user import get_user
from bot.filters.isUser import IsUser
from bot.keyboards.inline import get_callback_btns
from bot.filters.permission_filter import PermissionFilter

router = Router()
router.message.filter(F.chat.type == "private")
router.message.filter(IsUser())
# router.message.filter(PermissionFilter("can_manage_debts"))

class FSMDebt(StatesGroup):
    debet = State()


@router.callback_query(F.data.startswith("edit_debt_"))
async def manage_debts_meun(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    data_parts = callback.data.split('_')
    user_id = int(data_parts[2])
    user = await get_user(session, user_id)
    debt = await get_debt(session, user.tg_id)
    # if debt.amount == 0:
    #     debt.amount = "0"
    
    await callback.answer("Долги")
    await callback.message.edit_caption(
        caption=(
            f"💳 Долг пользователя {user.game_username} составляет:'{str(debt.amount)}'\n\n"
            f"➖ Чтобы уменьшить долг, отправьте сообщение: '-200'\n"
            f"➕ Чтобы увеличить долг, отправьте сообщение: '+100'"
        ),
        reply_markup=get_callback_btns(
            btns={
                "Отмена": "admin_menu"
            },
            sizes=(2, 1, 1)
        )
    )
    await state.set_state(FSMDebt.debet)
    await state.update_data(user=user, debt=debt)


@router.message(StateFilter(FSMDebt.debet))
async def process_debet(message: Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    user = data['user']
    debt = data['debt']
    msg = message.text
    amount = int(msg.lstrip("+-"))
    
    if msg.startswith('+'):
        debt.amount += amount
        await update_debt(session, debt.id, {"amount": debt.amount})
        await message.answer(
            f"Долг пользователя {user.game_username} изменен на '{debt.amount}'",
            reply_markup=get_callback_btns(
                btns={
                    "Назад": f"edit_debt_{user.tg_id}"
                },
                sizes=(2, 1, 1)
            )
        )
        await state.clear()
    elif msg.startswith('-'):
        debt.amount -= amount
        await update_debt(session, debt.id, {"amount": debt.amount})
        await message.answer(
            f"Долг пользователя {user.game_username} изменен на '{debt.amount}'",
            reply_markup=get_callback_btns(
                btns={
                    "Назад": f"edit_debt_{user.tg_id}"
                },
                sizes=(2, 1, 1)
            )
        )
        await state.clear()
