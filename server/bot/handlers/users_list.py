from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import Router, F
from aiogram.types import CallbackQuery, InputMediaPhoto, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.filters.isUser import IsUser
from bot.filters.permission_filter import PermissionFilter
from bot.database.queries.user import get_user, get_users, update_user, update_user_role
from bot.database.queries.role import get_role, get_role_by_name, get_roles
from bot.keyboards.inline import get_callback_btns
from bot.utils.paginator import Paginator

router = Router()
router.message.filter(IsUser())
router.message.filter(F.chat.type == "private")


USERS_PER_PAGE = 8

def pages(paginator: Paginator):
    btns = {}
    if paginator.has_previous():
        btns["◀ Пред."] = paginator.page - 1
    if paginator.has_next():
        btns["След. ▶"] = paginator.page + 1
    return btns


@router.callback_query(
    PermissionFilter(["can_change_role", "can_confirm_guests", "can_ban_and_unban_users"]), 
    F.data.startswith("users_page_")
)
async def users_list(callback: CallbackQuery, session: AsyncSession):
    data_parts = callback.data.split('_')
    page = int(data_parts[2]) if len(data_parts) > 2 and data_parts[2].isdigit() else 1

    users = await get_users(session)
    paginator = Paginator(users, page=page, per_page=USERS_PER_PAGE)

    page_users = paginator.get_page()
    if not page_users:
        await callback.message.edit_text("Нет пользователей для отображения.", parse_mode="HTML")
        return

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
        await callback.message.edit_text(
            text=caption,
            reply_markup=kb,
            parse_mode="HTML"
        )
    await callback.answer()


async def build_user_keyboard(page_users, paginator, page, session):
    size = ()
    btns = {}
    
    for user in page_users:
        role = await get_role_by_name(session, user.role)
        user_btn_text = f"{user.game_username} | @{user.username} | {role.title}"
        btns[user_btn_text] = f"view_profile_{user.tg_id}_page_{page}"
        size += (1, )

    navigation_btns = pages(paginator)
    if navigation_btns:
        for text, callback_page in navigation_btns.items():
            btns[text] = f"users_page_{callback_page}"
        
        if len(navigation_btns) > 1:
            size += (2,)
        else:
            size += (1,)

    btns["В админку"] = "admin_menu"
    size += (1, )

    return get_callback_btns(btns=btns, sizes=size)


@router.callback_query(
    PermissionFilter(["can_change_role", "can_confirm_guests", "can_ban_and_unban_users"]), 
    F.data.startswith("view_profile_")
)
async def view_profile(callback: CallbackQuery, session: AsyncSession):
    data_parts = callback.data.split('_')
    editor = await get_user(session, tg_id=callback.from_user.id)
    editor_role = await get_role_by_name(session, editor.role)
    user = await get_user(session, tg_id=data_parts[2])
    role = await get_role_by_name(session, user.role)
    btns = {}

    if editor_role.can_change_role:
        btns["Изменить роль"] = f"change_role_{user.tg_id}"
    if editor_role.can_ban_and_unban_users:
        btns["Забанить"] = f"ban_menu_{user.tg_id}"
    if editor_role.can_manage_debts:
        btns["Долги"] = f"edit_debt_{user.tg_id}"

    btns["Назад"] = f"users_page_{int(data_parts[4]) if len(data_parts) > 4 and data_parts[4].isdigit() else 1}"
    
    kb = get_callback_btns(btns=btns, sizes=(1,))
    if callback.message.photo:
        await callback.message.edit_media(
            media=InputMediaPhoto(
                media="https://imgur.com/KeDH3ft",
                caption=(
                    f"<b>Имя:</b> {user.game_username}\n"
                    f"<b>Ник:</b> @{user.username}\n"
                    f"<b>Роль:</b> {role.title}"
                ),
                parse_mode="HTML"
            ),
            reply_markup=kb
        )
    else:
        await callback.message.edit_text(
            text=(
                f"<b>Имя:</b> {user.game_username}\n"
                f"<b>Ник:</b> @{user.username}\n"
                f"<b>Роль:</b> {role.title}"
            ),
            parse_mode="HTML",
            reply_markup=kb,
        )
        await callback.answer()


@router.callback_query(
    PermissionFilter(["can_change_role"]), 
    F.data.startswith("change_role_")
)
async def change_role(callback: CallbackQuery, session: AsyncSession):
    data_parts = callback.data.split('_')
    user = await get_user(session, tg_id=data_parts[2])
    the_role = await get_role_by_name(session, user.role)
    roles = await get_roles(session)
    btns={}
    size=()

    
    for role in roles:
        # kb.add(InlineKeyboardButton(text=role.title, callback_data=f"changing_role_{user.tg_id}_{role.id}"))
        btns[f"{role.title}"] = f"changing_role_{user.tg_id}_{role.id}"
        size += (2,)
        
    
    # kb.add(InlineKeyboardButton(text="Назад", callback_data=f"view_profile_{user.tg_id}"))
    btns["Назад"] = f"view_profile_{user.tg_id}"
    size += (1,)
    
    kb = get_callback_btns(
        btns=btns,
        sizes=size
    )
    
    if callback.message.photo:
        await callback.message.edit_media(
            media=InputMediaPhoto(
                media="https://imgur.com/KeDH3ft",
                caption=(
                    f"<b>Имя:</b> {user.game_username}\n"
                    f"<b>Ник:</b> @{user.username}\n"
                    f"<b>Роль:</b> {the_role.title}"
                ),
                parse_mode="HTML"
            ),
            reply_markup=kb
        )
    else:
        await callback.message.edit_text(
            text=(
                f"<b>Имя:</b> {user.game_username}\n"
                f"<b>Ник:</b> @{user.username}\n"
                f"<b>Роль:</b> {the_role.title}"
            ),
            parse_mode="HTML",
            reply_markup=kb
        )
        await callback.answer()


@router.callback_query(
    PermissionFilter(["can_change_role"]),
    F.data.startswith("changing_role_")
)
async def change_role_to(callback: CallbackQuery, session: AsyncSession):
    data_parts = callback.data.split('_')
    user = await get_user(session, tg_id=data_parts[2])
    role_id = data_parts[3]

    await update_user_role(session, user.tg_id, role_id)
    await view_profile(callback, session)


@router.callback_query(
    PermissionFilter(["can_ban_and_unban_users"]),
    F.data.startswith("ban_menu_")
)
async def ban_menu(callback: CallbackQuery, session: AsyncSession):
    data_parts = callback.data.split('_')
    target_user_id = await get_user(session, tg_id=data_parts[2])
    
    btns = {}
    if target_user_id.is_baned:
        btns["Разбанить"] = f"unban_{target_user_id}"
    if not target_user_id.is_baned:
        btns["Забанить"] = f"ban_{target_user_id}"
        
    btns["Назад"] = f"view_profile_{target_user_id}"
    
    await callback.message.answer(
        text="Выберите действие:",
        reply_markup=get_callback_btns(
            btns=btns,
            sizes=(2, 2, 1)
        )
    )


@router.callback_query(
    PermissionFilter(["can_ban_and_unban_users"]),
    F.data.startswith("ban_")
)
async def ban_user(callback: CallbackQuery, session: AsyncSession):
    data_parts = callback.data.split('_')
    target_user_id = data_parts[1]

    await update_user(session, target_user_id, is_banned=True)
    await callback.message.edit_text(
        text="Пользователь забанен."
    )


@router.callback_query(
    PermissionFilter(["can_ban_and_unban_users"]),
    F.data.startswith("unban_")
)
async def unban_user(callback: CallbackQuery, session: AsyncSession):
    data_parts = callback.data.split('_')
    target_user_id = data_parts[1]

    await update_user(session, target_user_id, is_banned=False)
    await callback.message.edit_text(
        text="Пользователь разбанен."
    )
