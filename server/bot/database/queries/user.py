import logging

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from bot.database.models import User

logging.basicConfig(level=logging.INFO)

async def create_user(session: AsyncSession, data: dict):
    try:
        user = User(
            tg_id = data["tg_id"],
            game_username = data["game_username"],
            username = data["username"],
            firstname = data["firstname"],
            lastname = data["lastname"],
            role = data["role"],
        )
        session.add(user)
        await session.commit()
        logging.info(f"Create user successful: {user}")
        return user
    except SQLAlchemyError as e:
        logging.error(f"Create user error:{e}")
        await session.rollback()
        return False


async def get_user(session: AsyncSession, tg_id: int):
    try:
        query = select(User).where(User.tg_id == tg_id)
        result = await session.execute(query)
        user = result.scalar()
        if user:
            logging.info("")
            return user
        else:
            logging.warning("")
            return False
    except SQLAlchemyError as e:
        logging.error(f"error:{e}")
        await session.rollback()
        return False


async def get_user_by_id(session: AsyncSession, id: int):
    try:
        query = select(User).where(User.id == id)
        result = await session.execute(query)
        user = result.scalar()
        if user:
            logging.info("")
            return user
        else:
            logging.warning("")
            return False
    except SQLAlchemyError as e:
        logging.error(f"error:{e}")
        await session.rollback()
        return False


async def get_user_by_game_username(session: AsyncSession, game_username: str):
    try:
        query = select(User).where(User.game_username == game_username)
        result = await session.execute(query)
        user = result.scalar()
        if user:
            logging.info("")
            return user
        else:
            logging.warning("")
            return False
    except SQLAlchemyError as e:
        logging.error(f"error:{e}")
        await session.rollback()
        return False


async def get_guest_users(session: AsyncSession):
    try:
        query = select(User).where(User.role == "GUEST" and User.is_baned == False)
        result = await session.execute(query)
        users = result.scalars().all()
        logging.info("")
        return users
    except SQLAlchemyError as e:
        logging.error(f"error:{e}")
        await session.rollback()
        return False


async def get_users(session: AsyncSession):
    try:
        query = select(User)
        result = await session.execute(query)
        users = result.scalars().all()
        logging.info("")
        return users
    except SQLAlchemyError as e:
        logging.error(f"error:{e}")
        await session.rollback()
        return False

async def update_user(session: AsyncSession, data: dict):
    try:
        query = (
            update(User)
            .where(User.tg_id == data["tg_id"])
            .values(
                game_username = data["game_username"],
                username = data["username"],
                firstname = data["firstname"],
                lastname = data["lastname"],
                role = data["role"],
            )
        )
        result = await session.execute(query)
        if result:
            await session.commit()
            logging.info("")
            return result
        else:
            logging.warning("")
            return False
    except SQLAlchemyError as e:
        logging.error(f"error:{e}")
        await session.rollback()
        return False


async def update_user_role(session: AsyncSession, user_tg_id: int, role_id: int):
    try:
        query = (
            update(User)
            .where(User.tg_id == user_tg_id)
            .values(
                role = role_id,
            )
        )
        result = await session.execute(query)
        if result:
            await session.commit()
            logging.info("")
            return result
        else:
            logging.warning("")
            return False
    except SQLAlchemyError as e:
        logging.error(f"error:{e}")
        await session.rollback()
        return False

async def delete_user(session: AsyncSession, tg_id: int):
    try:
        query = delete(User).where(User.tg_id == tg_id)
        await session.execute(query)
        await session.commit()
        logging.info(f"Delete user with tg_id:{tg_id} successful")
        return
    except SQLAlchemyError as e:
        logging.error(f"Delete user error:{e}")
        await session.rollback()
        return False


async def delete_user_by_id(session: AsyncSession, id: int):
    try:
        query = delete(User).where(User.id == id)
        await session.execute(query)
        await session.commit()
        logging.info(f"Delete user with id:{id} successful")
        return
    except SQLAlchemyError as e:
        logging.error(f"Delete user error:{e}")
        await session.rollback()
        return False

async def update_user_bun(session: AsyncSession, tg_id: int, is_baned: bool):
    try:
        query = (
            update(User)
            .where(User.tg_id == tg_id)
            .values(
                is_baned = is_baned,
            )
        )
        result = await session.execute(query)
        if result:
            await session.commit()
            logging.info("")
            return result
        else:
            logging.warning("")
            return False
    except SQLAlchemyError as e:
        logging.error(f"error:{e}")
        await session.rollback()
        return False
