from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.filters import CommandStart, StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

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
router.message.filter(PermissionFilter("can_confirm_guests"))
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
    
    for user in page_users:
        role = await get_role_by_name(session, user.role)
        user_btn_text = f"{user.game_username} | @{user.username}"
        btns[user_btn_text] = f"guest_profile_{user.tg_id}_page_{page}"
        size += (1, )

    navigation_btns = pages(paginator)
    if navigation_btns:
        for text, callback_page in navigation_btns.items():
            btns[text] = f"users_page_{callback_page}"
        
        if len(navigation_btns) > 1:
            size += (2,)
        else:
            size += (1,)

    btns["Назад"] = "admin_menu"
    size += (1, )

    return get_callback_btns(btns=btns, sizes=size)


@router.callback_query(F.data == "guest_menu_")
async def confirm_guest(callback:CallbackQuery, session: AsyncSession):
    data_parts = callback.data.split('_')
    page = int(data_parts[2]) if len(data_parts) > 2 and data_parts[2].isdigit() else 1
    
    banner = await orm_get_banner_from_title(session, "confirm_guest")
    guests = await get_guest_users(session)
    
    paginator = Paginator(guests, page=page, per_page=USERS_PER_PAGE)
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


@router.callback_query(F.data.startswith("guest_profile_"))
async def guest_profile(callback:CallbackQuery, session: AsyncSession):
    data_parts = callback.data.split('_')
    tg_id = int(data_parts[2])
    page = int(data_parts[4]) if len(data_parts) > 4 and data_parts[4].isdigit() else 1

    guest = await get_user(session, tg_id)
    
    guest_photo = await bot.get_user_profile_photos(tg_id)
    if guest_photo and guest_photo.photos:
        guest_photo = guest_photo.photos[0][-1].file_id
    else:
        guest_photo = "https://coenterprises.com.au/wp-content/uploads/2018/02/male-placeholder-image.jpeg"
    
    caption = (
        f"Ник в аве: {guest.game_username}\n"
        f"Имя: {guest.username}\n"
        f"Telegram ID: {guest.tg_id}\n"
    )

    kb = get_callback_btns(
        btns={
            "🟢 Подтвердить": f"confirm_guest_{guest.tg_id}",
            "🔴 Отклонить": f"reject_guest_{guest.tg_id}",
            "◀ Назад": f"guest_menu_{page}",
            "В админку": "admin_menu"
        },
        sizes=(1, )
    )

    await callback.answer()
    await callback.message.edit_media(
        InputMediaPhoto(
            media=guest_photo,
            caption=caption,
        ),
        parse_mode="HTML",
        reply_markup=kb
    )


@router.callback_query(F.data.startswith("confirm_guest_"))
async def confirm_guest(callback:CallbackQuery, session: AsyncSession):
    data_parts = callback.data.split('_')
    tg_id = int(data_parts[2])

    guest = await get_user(session, tg_id)
    await update_user(
        session, 
        data={
            "tg_id": guest.tg_id,
            "username": guest.username,
            "firstname": guest.firstname,
            "lastname": guest.lastname,
            "game_username": guest.game_username,
            "role": "USER"
        }
    )
    user = await get_user(session, tg_id)
    
    
    await bot.send_message(
        chat_id=guest.tg_id,
        text=f"Регистрация прошла успешно! Рады познакомиться, {user.game_username}. Не забудьте вступить в нашу беседу: (ссылка)",
    )
    
    
    role = await get_role_by_name(session, user.role)
    
    kb = await main_menu_btns(role)
    banner = await orm_get_banner_from_title(session, "Main")

    await bot.send_photo(
        chat_id=guest.tg_id,
        photo=banner.image,
        caption=banner.description.format(first_name = user.firstname),
        reply_markup=kb
    )

    guest_photo = await bot.get_user_profile_photos(tg_id)
    if guest_photo and guest_photo.photos:
        guest_photo = guest_photo.photos[0][-1].file_id
    else:
        guest_photo = "https://coenterprises.com.au/wp-content/uploads/2018/02/male-placeholder-image.jpeg"

    await callback.answer()
    await callback.message.edit_media(
        InputMediaPhoto(
            media=guest_photo,
            caption="Пользователь успешно верефицирован!",
        ),
        parse_mode="HTML",
        reply_markup=get_callback_btns(
            btns={
                "◀ Назад": f"guest_menu_",
                "В админку": "admin_menu"
            },
            sizes=(1, 1)
        )
    )


@router.callback_query(F.data.startswith("reject_guest_"))
async def confirm_guest(callback:CallbackQuery, session: AsyncSession):
    data_parts = callback.data.split('_')
    tg_id = int(data_parts[2])

    await update_user_bun(session, tg_id, True)

    guest_photo = await bot.get_user_profile_photos(tg_id)
    if guest_photo and guest_photo.photos:
        guest_photo = guest_photo.photos[0][-1].file_id
    else:
        guest_photo = "https://coenterprises.com.au/wp-content/uploads/2018/02/male-placeholder-image.jpeg"

    await callback.answer()
    await callback.message.edit_media(
        InputMediaPhoto(
            media=guest_photo,
            caption="Пользователь успешно отклонен и забанен!",
        ),
        parse_mode="HTML",
        reply_markup=get_callback_btns(
            btns={
                "◀ Назад": f"guest_menu_",
                "В админку": "admin_menu"
            },
            sizes=(1, 1)
        )
    )


async def new_guest(session: AsyncSession):
    users = await get_users(session)
    for user in users:
        role = await get_role_by_name(session, user.role)
        if role.can_confirm_guests:
            await bot.send_message(
                chat_id=user.tg_id,
                text="Обнаружын новый гость, проверте его",
                reply_markup=get_callback_btns(
                    btns={
                        "Проверить": f"guest_menu_",
                        "В админку": "admin_menu"
                    },
                    sizes=(2,)
                )
            )
