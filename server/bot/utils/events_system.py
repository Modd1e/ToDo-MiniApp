import logging
from datetime import datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger, BaseTrigger
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.methods.send_message import SendMessage
from aiogram.methods.send_photo import SendPhoto

from bot.database.queries.debt import get_debt, get_user_debts, update_debt
from bot.database.queries.event import get_event, get_events
from bot.keyboards.inline import get_callback_btns
from bot.database.queries.event_confirm import create_event_confirmation, get_event_confirmation
from bot.database.queries.user import get_user, get_users
from bot.database.engine import session_maker


CONFIRMATION_TIME_LIMIT = timedelta(hours=3)
debt_amount = 100

async def init_events(scheduler, bot):
    async with session_maker() as session:
        events = await get_events(session)
        users = await get_users(session)

    for event in events:
        for job in scheduler.get_jobs():
            if job.id.startswith(f"event_{event.id}"):
                scheduler.remove_job(job.id)

        if event.is_active:
            for user in users:
                async def send_event_notification(user=user):
                    try:
                        keyboard = get_callback_btns(
                            btns={
                                "Подтвердить участие": f"confirm_event_{event.id}"
                            },
                            sizes=(1,)
                        )
                        await bot(SendPhoto(
                            chat_id=user.tg_id,
                            photo=event.image,
                            caption=(
                                f"<b>{event.title}</b>\n\n"
                                f"{event.description}"
                            ),
                            reply_markup=keyboard,
                            parse_mode="HTML"
                        ))
                        
                        async with session_maker() as session:
                            # user = await get_user(session, user.tg_id)
                            await create_event_confirmation(session, event.id, user.tg_id)

                        from main import scheduler
                        scheduler.add_job(
                            check_confirmation(event.id, user.tg_id, bot),
                            "date",
                            run_date=datetime.now() + CONFIRMATION_TIME_LIMIT,
                            # kwargs={"event_id": event.id, "user_tg_id": user.tg_id, "bot": bot}
                        )
                    except Exception as e:
                        logging.error(f"Failed to send notification: {e}")
                        
                scheduler.add_job(
                    send_event_notification,
                    trigger="date",
                    run_date=event.event_datetime,
                    id=f"event_{event.id}_user_{user.tg_id}",
                    # kwargs={
                    #     "user_tg_id": user.tg_id,
                    #     "event_image": event.image,
                    #     "event_title": event.title,
                    #     "event_description": event.description
                    # }
                )


async def check_confirmation(event_id, user_tg_id, bot):
    async with session_maker() as session:
        confirmation = await get_event_confirmation(session, event_id, user_tg_id)

        if confirmation and confirmation.confirmed:
            return

        if not confirmation or not confirmation.confirmed and confirmation.is_checked:
            print(f"User {user_tg_id} did not confirm event {event_id}. Adding debt...")
            await bot(SendMessage(chat_id=user_tg_id, text="Вы не подтвердили событие. Начислен долг."))
            i_debt = await get_user_debts(session, user_tg_id)
            await update_debt(session, i_debt.id, data={"amount": i_debt.amount + debt_amount})
