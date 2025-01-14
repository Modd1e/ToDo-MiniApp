from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
import logging

from bot.database.models import Role

logging.basicConfig(level=logging.INFO)


async def create_role(session: AsyncSession, data: dict):
    try:
        role = Role(
            title=data["title"],
            name=data["name"],
            can_use_default_func=data["can_use_default_func"],
            can_confirm_guests=data["can_confirm_guests"],
            can_manage_debts=data["can_manage_debts"],
            can_change_role=data["can_change_role"],
            can_ban_and_unban_users=data["can_ban_and_unban_users"],
            can_spam=data["can_spam"],
            can_sync_db=data["can_sync_db"],
            can_confirm_events=data["can_confirm_events"],
        )
        session.add(role)
        await session.commit()
        logging.info(f"Create role successful: {role}")
        return role
    except SQLAlchemyError as e:
        logging.error(f"Create role error: {e}")
        await session.rollback()
        return False


async def get_role(session: AsyncSession, id: int):
    try:
        query = select(Role).where(Role.id == id)
        result = await session.execute(query)
        role = result.scalar()
        return role
    except SQLAlchemyError as e:
        logging.error(f"Get role error: {e}")
        return False


async def get_role_by_name(session: AsyncSession, name: str):
    try:
        query = select(Role).where(Role.name == name)
        result = await session.execute(query)
        role = result.scalar()
        return role
    except SQLAlchemyError as e:
        logging.error(f"Get role error: {e}")
        return False

async def get_roles(session: AsyncSession):
    try:
        query = select(Role)
        result = await session.execute(query)
        roles = result.scalars().all()
        return roles
    except SQLAlchemyError as e:
        logging.error(f"Get roles error: {e}")
        return False


async def get_role_by_title(session: AsyncSession, title: str):
    try:
        query = select(Role).where(Role.title == title)
        result = await session.execute(query)
        role = result.scalar()
        return role
    except SQLAlchemyError as e:
        logging.error(f"Get role by title error: {e}")
        return False


async def update_role(session: AsyncSession, id: int, data: dict):
    try:
        query = (
            update(Role)
            .where(Role.id == id)
            .values(
                title=data["title"],
                name=data["name"],
                can_use_default_func=data["can_use_default_func"],
                can_confirm_guests=data["can_confirm_guests"],
                can_manage_debts=data["can_manage_debts"],
                can_change_role=data["can_change_role"],
                can_ban_and_unban_users=data["can_ban_and_unban_users"],
                can_spam=data["can_spam"],
                can_sync_db=data["can_sync_db"],
                can_confirm_events=data["can_confirm_events"],
                
            )
        )
        result = await session.execute(query)
        await session.commit()
        return result
    except SQLAlchemyError as e:
        logging.error(f"Update role error: {e}")
        await session.rollback()
        return False

async def delete_role(session: AsyncSession, id: int):
    try:
        query = delete(Role).where(Role.id == id)
        await session.execute(query)
        await session.commit()
        logging.info(f"Delete role with id: {id} successful")
    except SQLAlchemyError as e:
        logging.error(f"Delete role error: {e}")
        await session.rollback()
