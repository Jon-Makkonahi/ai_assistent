import enum
from datetime import datetime
from typing import List, Optional

from sqlalchemy import String, Enum, Integer, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """
    Базовый класс для объявления моделей данных в декларативном стиле.
    Классы, которые наследуются от этого класса, будут сопоставляться с таблицами в базе данных.
    """
    pass


class TaskStatus(enum.Enum):
    """Статусы выполнения задачи."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class SenderType(enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"),
                                         nullable=False)
    task_id: Mapped[Optional[int]] = mapped_column(ForeignKey("tasks.id"),
                                                   nullable=True)

    sender: Mapped[SenderType] = mapped_column(Enum(SenderType),
                                               nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)

    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    user: Mapped["User"] = relationship("User", back_populates="messages")
    task: Mapped[Optional["Task"]] = relationship("Task",
                                                  back_populates="messages")


class Task(Base):
    """ORM-модель таблицы задач."""
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    task_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"),
                                         nullable=False)
    input_data: Mapped[str] = mapped_column(String)
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus), default=TaskStatus.PENDING
    )
    result: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )

    user: Mapped["User"] = relationship("User", back_populates="tasks")
    messages: Mapped[list["Message"]] = relationship("Message",
                                                     back_populates="task")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    telegram_id: Mapped[str] = mapped_column(unique=True, index=True)
    username: Mapped[Optional[str]]
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="user")
    messages: Mapped[list["Message"]] = relationship("Message",
                                                     back_populates="user")
