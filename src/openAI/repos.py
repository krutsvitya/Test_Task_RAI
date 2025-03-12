from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from config.models import Chat, User


class OpenAIRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_chat_by_id(self, chat_id: int):
        result = await self.session.execute(
            select(Chat).options(selectinload(Chat.messages)).filter(Chat.id == chat_id)
        )
        chat = result.unique().scalar_one_or_none()

        return chat

    async def get_all_chats(self, user_id: int):
        """Получает все чаты с их сообщениями для конкретного пользователя."""
        result = await self.session.execute(
            select(Chat)
            .options(selectinload(Chat.messages))
            .filter(Chat.user_id == user_id)
        )
        chats = result.scalars().all()
        return chats
