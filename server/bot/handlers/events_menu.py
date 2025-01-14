from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import Router, F
from aiogram.types import CallbackQuery, InputMediaPhoto, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.filters.isUser import IsUser
from bot.filters.permission_filter import PermissionFilter
from bot.database.queries.user import get_user, get_users, update_user, update_user_role
from bot.database.queries.event_confirm import get_unconfirmed_event_for_user, get_unconfirmed_event_for_user_and_event_id
from bot.database.queries.event import get_event
from bot.keyboards.inline import get_callback_btns
from bot.utils.paginator import Paginator

router = Router()
router.message.filter(IsUser())
router.message.filter(F.chat.type == "private")


ITEMS_PER_PAGE = 8

def pages(paginator: Paginator):
    btns = {}
    if paginator.has_previous():
        btns["◀ Пред."] = paginator.page - 1
    if paginator.has_next():
        btns["След. ▶"] = paginator.page + 1
    return btns

async def build_user_keyboard(page_unconfirmed_events, paginator, page, session):
    size = ()
    btns = {}
    
    for unconfirmed_event in page_unconfirmed_events:
        event = await get_event(session, unconfirmed_event.event_id)
        user_btn_text = f"{event.title}"
        btns[user_btn_text] = f"view_unconfirmed_events_{event.id}_user_{unconfirmed_event.user_tg_id}_page_{page}"
        size += (1, )

    navigation_btns = pages(paginator)
    if navigation_btns:
        for text, callback_page in navigation_btns.items():
            btns[text] = f"events_menu_{callback_page}"
        
        if len(navigation_btns) > 1:
            size += (2,)
        else:
            size += (1,)

    btns["На главную"] = "main_menu"
    size += (1, )

    return get_callback_btns(btns=btns, sizes=size)


@router.callback_query(F.data.startswith("events_menu_"))
async def users_list(callback: CallbackQuery, session: AsyncSession):
    data_parts = callback.data.split('_')
    page = int(data_parts[2]) if len(data_parts) > 2 and data_parts[2].isdigit() else 1

    unconfirmed_events = await get_unconfirmed_event_for_user(session, callback.from_user.id)
    if not unconfirmed_events:
        await callback.message.edit_caption("У тебя нет невыполненных событий, продолжай в том же духе!", parse_mode="HTML", reply_markup=
                                            get_callback_btns(btns={"На главную": "main_menu"}))
        return

    paginator = Paginator(array=unconfirmed_events, page=page, per_page=ITEMS_PER_PAGE)
    page_users = paginator.get_page()
    

    caption = f"<strong>Страница {paginator.page} из {paginator.pages}</strong>"
    kb = await build_user_keyboard(page_users, paginator, page, session)

    if callback.message.photo:
        await callback.message.edit_media(
            media=InputMediaPhoto(
                media="https://imgur.com/KeDH3ft",
                caption=caption,
                parse_mode="HTML"
            ),
            reply_markup=kb
        )
    else:
        await callback.message.edit_caption(
            text=caption,
            reply_markup=kb,
            parse_mode="HTML"
        )
    await callback.answer()


@router.callback_query(F.data.startswith("view_unconfirmed_events_"))
async def view_unconfirmed_events(callback: CallbackQuery, session: AsyncSession):
    data_parts = callback.data.split('_') # 3, 5, 7
    event_id = int(data_parts[3]) if len(data_parts) > 3 and data_parts[3].isdigit() else None
    page = int(data_parts[7]) if len(data_parts) > 7 and data_parts[7].isdigit() else 1
    unconfirmed_event = get_unconfirmed_event_for_user_and_event_id(session, callback.from_user.id, event_id)
    event = await get_event(session, event_id)

    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=event.image,
            caption=f"Подтвердите участие в событии: {event.title}\n\n{event.description}",
            parse_mode="HTML"
        ),
        reply_markup=get_callback_btns(
            btns={
                "Подтвердить": f"confirm_event_{event_id}_user_{callback.from_user.id}",
                "Назад": f"events_menu_{page}"  
            },
            sizes=(1, 1)
        )
    )
