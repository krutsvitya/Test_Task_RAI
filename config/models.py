from datetime import datetime

from sqlalchemy import (
    Integer,
    String,
    func,
    ForeignKey,
    TIMESTAMP,
    Column,
    DateTime
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from config.db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped["datetime"] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    chats = relationship("Chat", back_populates="user", cascade="all, delete", lazy="selectin")

class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, default="Новый чат")
    user_id = Column(Integer, ForeignKey("users.id"))

    messages = relationship("Message", back_populates="chat", cascade="all, delete", lazy="selectin")
    user = relationship("User", back_populates="chats")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id"))
    text = Column(String)
    sender = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

    chat = relationship("Chat", back_populates="messages")