from sqlalchemy.ext.asyncio import AsyncSession

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.filters import CommandStart, StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from bot.database.queries.event import get_event
from bot.database.queries.event_confirm import get_event_confirmation, get_unconfirmed_event, get_unconfirmed_events, update_event_confirmation
from bot.filters.isUser import IsUser
from bot.filters.permission_filter import PermissionFilter
from bot.handlers.handlers import main_menu_btns, main_menu_callback
from main import bot
from bot.database.queries.banner import orm_get_banner_from_title
from bot.database.queries.role import get_role_by_name
from bot.database.queries.user import get_guest_users, get_user, get_users, update_user, update_user_bun
from bot.keyboards.inline import get_callback_btns
from bot.utils.paginator import Paginator

router = Router()
router.message.filter(IsUser())
router.message.filter(PermissionFilter("can_confirm_events"))
router.message.filter(F.chat.type == "private")

USERS_PER_PAGE = 8

def pages(paginator: Paginator):
    btns = {}
    if paginator.has_previous():
        btns["◀ Пред."] = paginator.page - 1
    if paginator.has_next():
        btns["След. ▶"] = paginator.page + 1
    return btns



async def build_user_keyboard(page_users, paginator, page, session):
    size = ()
    btns = {}
    
    for unconf_event in page_users:
        event = await get_event(session, unconf_event.event_id)
        user = await get_user(session, unconf_event.user_tg_id)
        user_btn_text = f"{event.title} | @{user.username}"
        btns[user_btn_text] = f"viwe_unconf_event_{unconf_event.id}_page_{page}"
        size += (1, )

    navigation_btns = pages(paginator)
    if navigation_btns:
        for text, callback_page in navigation_btns.items():
            btns[text] = f"event_confirm_menu_{callback_page}"
        
        if len(navigation_btns) > 1:
            size += (2,)
        else:
            size += (1,)

    btns["Назад"] = "admin_menu"
    size += (1, )

    return get_callback_btns(btns=btns, sizes=size)


@router.callback_query(F.data.startswith("event_confirm_menu_"))
async def confirm_guest(callback:CallbackQuery, session: AsyncSession):
    data_parts = callback.data.split('_')
    page = int(data_parts[2]) if len(data_parts) > 2 and data_parts[2].isdigit() else 1
    
    banner = await orm_get_banner_from_title(session, "unconfirmed_events")
    unconfirmed_events = await get_unconfirmed_events(session)
    
    paginator = Paginator(unconfirmed_events, page=page, per_page=USERS_PER_PAGE)
    page_users = paginator.get_page()
    
    caption = f"<strong>Страница {paginator.page} из {paginator.pages}</strong>"
    kb = await build_user_keyboard(page_users, paginator, page, session)
    
    await callback.answer(banner.callback_answer)
    await callback.message.edit_media(
        InputMediaPhoto(
            media=banner.image,
            caption=f"{banner.description}\n\n{caption}",
        ),
        parse_mode="HTML",
        reply_markup=kb
    )


@router.callback_query(F.data.startswith("viwe_unconf_event_"))
async def guest_profile(callback:CallbackQuery, session: AsyncSession):
    data_parts = callback.data.split('_')
    unconfirm_event = get_unconfirmed_event(session, int(data_parts[3])) 
    page = int(data_parts[5]) if len(data_parts) > 5 and data_parts[5].isdigit() else 1

    user = await get_user(session, unconfirm_event.user_id )
    event = await get_event(session, unconfirm_event.event_id)
    
    caption = (
        f"ID события: {event.id}\n"
        f"Названия события: {event.title}\n"
        f"Описание события: {event.description}\n\n"
        
        f"TG_ID пользователя: {user.tg_id}\n"
        f"Ник пользователя: {user.game_username}\n"
        f"Имя пользователя: {user.firstname}\n\n"
        
        f"Текст подпвирждения: {unconfirm_event.proof_msg or 'none'}\n"
    )

    kb = get_callback_btns(
        btns={
            "🟢 Подтвердить": f"confirm_unconfirm_event_{unconfirm_event.id}",
            "🔴 Отклонить": f"reject_unconfirm_event_{unconfirm_event.id}",
            "◀ Назад": f"guest_menu_{page}",
            "В админку": "admin_menu"
        },
        sizes=(1, )
    )

    await callback.answer()
    if unconfirm_event.proof_img:
        await callback.message.answer_photo(
            InputMediaPhoto(
                media=unconfirm_event.proof_img,
                caption=caption,
            ),
            parse_mode="HTML",
            reply_markup=kb
        )
    elif unconfirm_event.proof_msg:
        await callback.message.answer(
            text=caption,
            parse_mode="HTML",
            reply_markup=kb
        )
    else:
        await callback.message.answer(
            text="error"
        )


@router.callback_query(F.data.startswith("confirm_unconfirm_event_"))
async def confirm_guest(callback:CallbackQuery, session: AsyncSession):
    data_parts = callback.data.split('_')
    unconfirm_event = await update_event_confirmation(
        session, 
        int(data_parts[3]),
        data={
            "is_confirmed": True,
            "is_checked": True

        }
    )
    
    await bot.send_message(
        chat_id=unconfirm_event.user_tg_id,
        text="Событие подтверждено!",
    )
    

    await callback.answer()
    await callback.message.answer(
        "Событие подтверждено",
        parse_mode="HTML",
        reply_markup=get_callback_btns(
            btns={
                "◀ Назад": f"event_confirm_menu_",
                "В админку": "admin_menu"
            },
            sizes=(1, 1)
        )
    )


@router.callback_query(F.data.startswith("reject_unconfirm_event_"))
async def confirm_guest(callback:CallbackQuery, session: AsyncSession):
    data_parts = callback.data.split('_')
    unconfirm_event = await update_event_confirmation(
        session, 
        int(data_parts[3]),
        data={
            "is_confirmed": False,
            "is_checked": True
        }
    )
    
    await bot.send_message(
        chat_id=unconfirm_event.user_tg_id,
        text="Событие отклонено начислен долг!",
    )
    

    await callback.answer()
    await callback.message.answer(
        "Событие подтверждено",
        parse_mode="HTML",
        reply_markup=get_callback_btns(
            btns={
                "◀ Назад": f"event_confirm_menu_",
                "В админку": "admin_menu"
            },
            sizes=(1, 1)
        )
    )
