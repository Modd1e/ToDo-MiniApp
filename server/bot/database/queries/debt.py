import logging

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from bot.database.models import Debt

logging.basicConfig(level=logging.INFO)


async def create_debt(session: AsyncSession, data: dict):
    try:
        debt = Debt(
            amount=data.get("amount"),
            user_id=data.get("user_id"),
        )
        session.add(debt)
        await session.commit()
        logging.info(f"Create debt successful: {debt}")
        return debt
    except SQLAlchemyError as e:
        logging.error(f"Create debt error: {e}")
        await session.rollback()
        return False

async def get_debt(session: AsyncSession, id: int):
    try:
        query = select(Debt).where(Debt.user_id == id)
        result = await session.execute(query)
        debt = result.scalar()
        return debt
    except SQLAlchemyError as e:
        logging.error(f"Get debt error: {e}")
        return False

async def get_user_debts(session: AsyncSession, user_id: int):
    try:
        query = select(Debt).where(Debt.user_id == user_id)
        result = await session.execute(query)
        debts = result.scalars().all()
        return debts
    except SQLAlchemyError as e:
        logging.error(f"Get user debts error: {e}")
        return False

async def update_debt(session: AsyncSession, id: int, data: dict):
    try:
        query = (
            update(Debt)
            .where(Debt.id == id)
            .values(
                amount=data.get("amount"),
                user_id=data.get("user_id"),
            )
        )
        result = await session.execute(query)
        await session.commit()
        return result
    except SQLAlchemyError as e:
        logging.error(f"Update debt error: {e}")
        await session.rollback()
        return False

async def delete_debt(session: AsyncSession, id: int):
    try:
        query = delete(Debt).where(Debt.id == id)
        await session.execute(query)
        await session.commit()
        logging.info(f"Delete debt with id: {id} successful")
    except SQLAlchemyError as e:
        logging.error(f"Delete debt error: {e}")
        await session.rollback()
