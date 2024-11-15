from typing import Optional

from sqlalchemy import Integer, String, Boolean, ForeignKey, Enum
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship

class TaskStatus(Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"

class Base(DeclarativeBase):
    pass
class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)

class Task(Base):
    __tablename__ = 'tasks'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, index=True)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    complete: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[TaskStatus] = mapped_column(Enum, default=TaskStatus.PENDING)

    photos: Mapped["Photo"] = relationship("Photo", back_populates="task")

class Photo(Base):
    __tablename__ = 'photos'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    filename: Mapped[str] = mapped_column(String, index=True)  # Название файла в MinIO
    url: Mapped[str] = mapped_column(String)  # Ссылка на фото в MinIO
    task_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("tasks.id"))  # Связь с таблицей заданий

    task: Mapped[Task] = relationship("Task", back_populates="photos")
