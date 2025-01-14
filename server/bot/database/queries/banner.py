import logging

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from bot.database.models import Banner

logging.basicConfig(level=logging.INFO)


async def orm_add_banner(session: AsyncSession, data: dict) -> bool:
    try:
        banner = Banner(
            title=data["title"],
            image=data["image"],
            callback_answer=data["callback_answer"],
            description=data["description"]
        )
        session.add(banner)
        await session.commit()
        logging.info(f"Банер добавлен: {banner}")
        return True
    except SQLAlchemyError as e:
        logging.error(f"Ошибка при добавлении банера: {e}")
        await session.rollback()
        return False


async def orm_get_banners(session: AsyncSession) -> list[Banner]:
    query = select(Banner)
    result = await session.execute(query)
    banners = result.scalars().all()
    logging.info(f"Получено {len(banners)} банеров.")
    return banners


async def orm_get_banner(session: AsyncSession, banner_id: int) -> Banner | None:
    try:
        query = select(Banner).where(Banner.id == banner_id)
        result = await session.execute(query)
        banner = result.scalar()
        logging.info(f"Получен банер с ID: {banner_id}")
        return banner
    except SQLAlchemyError as e:
        logging.error(f"Банер с ID: {banner_id} не найден.")
        await session.rollback()
        return False


async def orm_get_banner_from_title(session: AsyncSession, title: str) -> Banner | None:
    try:
        query = select(Banner).where(Banner.title == title)
        result = await session.execute(query)
        banner = result.scalar()
        logging.info(f"Получен банер с title: {title}")
        return banner
    except SQLAlchemyError as e:
        logging.error(f"Банер с title: {title} не найден.")
        await session.rollback()
        return False


async def orm_update_banner(session: AsyncSession, banner_id: int, data: dict) -> bool:
    try:
        query = (
            update(Banner)
            .where(Banner.id == banner_id)
            .values(
                title=data["title"],
                image=data["image"],
                callback_answer=data["callback_answer"],
                description=data["description"]
            )
        )
        result = await session.execute(query)
        if result.rowcount > 0:
            await session.commit()
            logging.info(f"Банер с ID: {banner_id} обновлен.")
            return True
        else:
            logging.warning(f"Банер с ID: {banner_id} не найден.")
            return False
    except SQLAlchemyError as e:
        logging.error(f"Ошибка при обновлении банера {banner_id}: {e}")
        await session.rollback()
        return False


async def orm_delete_banner(session: AsyncSession, banner_id: int) -> bool:
    try:
        query = delete(Banner).where(Banner.id == banner_id)
        result = await session.execute(query)
        if result.rowcount > 0:
            await session.commit()
            logging.info(f"Банер с ID: {banner_id} удален.")
            return True
        else:
            logging.warning(f"Банер с ID: {banner_id} не найден.")
            return False
    except SQLAlchemyError as e:
        logging.error(f"Ошибка при удалении банера {banner_id}: {e}")
        await session.rollback()
        return False
