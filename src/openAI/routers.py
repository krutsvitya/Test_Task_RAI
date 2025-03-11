import os
import re

import openai
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter, HTTPException, Depends
from dotenv import load_dotenv
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config.db import get_db
from config.models import Chat, Message
from src.auth.schemas import MessageRequest, ChatRenameRequest
from src.auth.utils import get_current_user
from src.openAI.repos import OpenAIRepository
from src.openAI.scraping_utils import get_website_content, analyze_with_chatgpt

load_dotenv()
router = APIRouter()
templates = Jinja2Templates(directory="templates")

api_key = os.getenv("OPENAI_SECRET_KEY")
if not api_key:
    raise ValueError("API-ключ OpenAI не найден в переменных окружения.")
client = openai.OpenAI(api_key=api_key)


@router.post("/chat/new")
async def create_chat(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Создает новый чат и возвращает его ID."""
    chat = Chat(name="Новый чат", user_id=current_user.id)
    db.add(chat)
    await db.commit()
    await db.refresh(chat)
    return {"chat_id": chat.id}


@router.get("/chat/{chat_id}")
async def get_chat_messages(
    chat_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Возвращает историю сообщений чата, если он принадлежит текущему пользователю."""
    ai_repos = OpenAIRepository(db)
    chat = await ai_repos.get_chat_by_id(chat_id)

    if not chat or chat.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Чат не найден")

    if not chat:
        raise HTTPException(status_code=404, detail="Чат не найден")

    messages = []
    for msg in chat.messages:
        messages.append({
            "id": msg.id,
            "text": msg.text,
            "sender": msg.sender,
            "timestamp": msg.timestamp.isoformat()
        })

    return {"chat_id": chat.id, "messages": messages}


@router.post("/chat/{chat_id}/send")
async def send_message(
    chat_id: int,
    message: MessageRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    result = await db.execute(select(Chat).filter(Chat.id == chat_id))
    chat = result.scalars().first()

    if not chat or chat.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Чат не найден")

    url_pattern = re.compile(r'https?://\S+')
    url_match = url_pattern.search(message.text)

    if url_match:
        url = url_match.group(0)
        site_text = get_website_content(url)
        bot_message_text = analyze_with_chatgpt(site_text, message.text)
    else:
        bot_message_text = analyze_with_chatgpt("", message.text)

    user_message = Message(chat_id=chat_id, text=message.text, sender="user")
    db.add(user_message)
    await db.commit()

    bot_message = Message(chat_id=chat_id, text=bot_message_text, sender="bot")
    db.add(bot_message)
    await db.commit()
    await db.refresh(bot_message)

    return {"response": bot_message_text}


@router.post("/chat/{chat_id}/rename")
async def rename_chat(
    chat_id: int,
    request: ChatRenameRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Переименовывает чат, если он принадлежит текущему пользователю."""
    result = await db.execute(select(Chat).filter(Chat.id == chat_id))
    chat = result.scalars().first()

    if not chat or chat.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Чат не найден")

    chat.name = request.name
    await db.commit()

    return {"status": "success", "message": "Чат успешно переименован"}


@router.get("/chats/list")
async def list_chats(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Возвращает список всех чатов с предпросмотром последнего сообщения для текущего пользователя."""
    ai_repos = OpenAIRepository(db)
    chats = await ai_repos.get_all_chats(current_user.id)

    chat_list = []
    for chat in chats:
        preview = "Новый чат"
        if chat.messages:
            user_messages = [msg for msg in chat.messages if msg.sender == "user"]
            if user_messages:
                sorted_messages = sorted(user_messages, key=lambda x: x.timestamp)
                first_message = sorted_messages[0].text
                preview = first_message[:25] + "..." if len(first_message) > 25 else first_message

        chat_list.append({
            "id": chat.id,
            "name": chat.name,
            "preview": preview
        })

    return {"chats": chat_list}


@router.delete("/chat/{chat_id}")
async def delete_chat(
    chat_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Удаляет чат и все его сообщения, если он принадлежит текущему пользователю."""
    result = await db.execute(select(Chat).filter(Chat.id == chat_id))
    chat = result.scalars().first()

    if not chat or chat.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Чат не найден")

    await db.delete(chat)
    await db.commit()

    return {"status": "success", "message": "Чат успешно удален"}



