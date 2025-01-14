from typing import Optional
from sqlalchemy import (
    Float, Integer, BigInteger, String, ForeignKey, DateTime, Boolean, Text, func
)
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column
from datetime import datetime

class Base(DeclarativeBase):
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class Banner(Base):
    __tablename__ = "banners"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    image: Mapped[str] = mapped_column(String(150))
    callback_answer: Mapped[str] = mapped_column(String(150))
    description: Mapped[str] = mapped_column(Text)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    game_username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    firstname: Mapped[str] = mapped_column(String(50), nullable=False)
    lastname: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    role: Mapped[str] = mapped_column(ForeignKey("roles.name"), nullable=False, default="GUEST")
    is_baned: Mapped[bool] = mapped_column(Boolean, default=False)


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)

    can_use_default_func: Mapped[bool] = mapped_column(Boolean, default=False)
    can_confirm_guests: Mapped[bool] = mapped_column(Boolean, default=False)
    can_manage_debts: Mapped[bool] = mapped_column(Boolean, default=False)
    can_change_role: Mapped[bool] = mapped_column(Boolean, default=False)
    can_ban_and_unban_users: Mapped[bool] = mapped_column(Boolean, default=False)
    can_spam: Mapped[bool] = mapped_column(Boolean, default=False)
    can_sync_db: Mapped[bool] = mapped_column(Boolean, default=False)
    can_confirm_events: Mapped[bool] = mapped_column(Boolean, default=False)


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    image: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    event_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class EventConfirmation(Base):
    __tablename__ = "event_confirmations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"), nullable=False)
    user_tg_id: Mapped[int] = mapped_column(ForeignKey("users.tg_id"), nullable=False)
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    is_checked: Mapped[bool] = mapped_column(Boolean, default=False)
    confirmation_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    proof_msg: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    proof_img: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)


class Debt(Base):
    __tablename__ = "debts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.tg_id"), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False, default=0)
