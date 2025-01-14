from sqlalchemy.ext.asyncio import AsyncSession

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.types.chat import Chat

from bot.filters.chat_types import ChatTypeFilter


router = Router()
router.message.filter(ChatTypeFilter(["group", "supergroup"]))


@router.message(Command("get_chat_id"))
async def get_chat_id(message: Message):
    await message.answer(f"{message.chat.type} | {message.chat.id}")
