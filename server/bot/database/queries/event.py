import logging

from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

from bot.database.models import Event

logging.basicConfig(level=logging.INFO)


async def create_event(session: AsyncSession, data: dict):
    try:
        event = Event(
            title=data["title"],
            description=data["description"],
            image=data["image"],
            event_datetime=data["event_datetime"],
            is_active=data["is_active"],
            # user_target=data["user_target"],
            # role_target=data["role_target"]
        )
        session.add(event)
        await session.commit()
        logging.info(f"Create event successful: {event}")
        return event
    except SQLAlchemyError as e:
        logging.error(f"Create event error: {e}")
        await session.rollback()
        return False


async def get_event(session: AsyncSession, id: int):
    try:
        query = select(Event).where(Event.id == id)
        result = await session.execute(query)
        event = result.scalar()
        if event:
            logging.info(f"Event found: {event}")
            return event
        else:
            logging.warning(f"No event found with ID {id}.")
            return False
    except SQLAlchemyError as e:
        logging.error(f"Error retrieving event: {e}")
        await session.rollback()
        return False


async def get_events(session: AsyncSession):
    try:
        query = select(Event)
        result = await session.execute(query)
        events = result.scalars().all()
        logging.info(f"Found {len(events)} events.")
        return events
    except SQLAlchemyError as e:
        logging.error(f"Error retrieving events: {e}")
        await session.rollback()
        return False


async def update_event(session: AsyncSession, id: int, data: dict):
    try:
        event = (
            update(Event)
            .where(Event.id == id)
            .values(
                title=data["title"],
                description=data["description"],
                image=data["image"],
                event_datetime=data["event_datetime"],
                is_active=data["is_active"],
                # user_target=data["user_target"],
                # role_target=data["role_target"]
            )
        )
        result = await session.execute(event)
        if result:
            await session.commit()
            logging.info(f"Update event successful: ID {id}")
            return result
        else:
            logging.warning(f"No event found with ID {id} to update.")
            return False
    except SQLAlchemyError as e:
        logging.error(f"Update event error: {e}")
        await session.rollback()
        return False


async def delete_event(session: AsyncSession, id: int):
    try:
        query = delete(Event).where(Event.id == id)
        await session.execute(query)
        await session.commit()
        logging.info(f"Delete event with ID {id} successful")
        return
    except SQLAlchemyError as e:
        logging.error(f"Delete event error:{e}")
        await session.rollback()
        return False
