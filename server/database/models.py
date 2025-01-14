from sqlalchemy import DateTime, ForeignKey, String, BigInteger, func
from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs


class Base(AsyncAttrs, DeclarativeBase):
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class User(Base):
    __tablename__ = 'users'
    
    id = mapped_column(BigInteger, primary_key=True)
    color_theme: Mapped[str] = mapped_column(String(32), default='DARK')


class Task(Base):
    __tablename__ = 'tasks'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(128))
    description: Mapped[str] = mapped_column(String(1024))
    is_completed: Mapped[bool] = mapped_column(default=False)
    user: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
