import logging

from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

from bot.database.models import EventConfirmation

logging.basicConfig(level=logging.INFO)


async def create_event_confirmation(session: AsyncSession, event_id: int, user_tg_id: int):
    try:
        confirmation = EventConfirmation(event_id=event_id, user_tg_id=user_tg_id)
        session.add(confirmation)
        await session.commit()
        return confirmation
    except Exception as e:
        logging.error(f"Error creating event confirmation: {e}")
        await session.rollback()
        return False


async def get_event_confirmation(session: AsyncSession, event_id: int, user_tg_id: int):
    try:
        query = select(EventConfirmation).where(EventConfirmation.event_id == event_id, EventConfirmation.user_tg_id == user_tg_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()
    except Exception as e:
        logging.error(f"Error getting event confirmation: {e}")
        return None

async def get_event_confirmation_by_id(session: AsyncSession, confirmation_id: int):
    try:
        query = select(EventConfirmation).where(EventConfirmation.id == confirmation_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()
    except Exception as e:
        logging.error(f"Error getting event confirmation by id: {e}")
        return None

async def update_event_confirmation(session: AsyncSession, confirmation_id: int, data: dict):
    try:
        query = update(EventConfirmation).where(EventConfirmation.id == confirmation_id).values(**data)
        await session.execute(query)
        await session.commit()
        return True
    except Exception as e:
        logging.error(f"Error updating event confirmation: {e}")
        await session.rollback()
        return False

async def get_unconfirmed_event_for_user(session: AsyncSession, user_tg_id: int):
    try:
        query = select(EventConfirmation).where(EventConfirmation.user_tg_id == user_tg_id, EventConfirmation.confirmed == False, EventConfirmation.is_checked == False)
        result = await session.execute(query)
        unconfirmed_events = result.scalars().all()
        return unconfirmed_events
    except Exception as e:
        logging.error(f"Error fetching unconfirmed event for user {user_tg_id}: {e}")
        return None

async def get_unconfirmed_events(session: AsyncSession):
    try:
        query = select(EventConfirmation).where(EventConfirmation.confirmed == False, EventConfirmation.is_checked == False)
        result = await session.execute(query)
        unconfirmed_events = result.scalars().all()
        return unconfirmed_events
    except Exception as e:
        logging.error(f"Error fetching unconfirmed event: {e}")
        return None

async def get_unconfirmed_event(session: AsyncSession, id:int):
    try:
        query = select(EventConfirmation).where(EventConfirmation.confirmed == False, EventConfirmation.id == id, EventConfirmation.is_checked == False)
        result = await session.execute(query)
        unconfirmed_events = result.scalars().all()
        return unconfirmed_events
    except Exception as e:
        logging.error(f"Error fetching unconfirmed event: {e}")
        return None
    

async def get_unconfirmed_event_for_user_and_event_id(session: AsyncSession, user_tg_id: int, event_id: int):
    try:
        query = select(EventConfirmation).where(
            EventConfirmation.user_tg_id == user_tg_id, 
            EventConfirmation.event_id == event_id, 
            EventConfirmation.confirmed == False,
            EventConfirmation.is_checked == False
        )
        result = await session.execute(query)
        unconfirmed_events = result.scalars().all()
        return unconfirmed_events
    except Exception as e:
        logging.error(f"Error fetching unconfirmed event for user {user_tg_id}: {e}")
        return None
