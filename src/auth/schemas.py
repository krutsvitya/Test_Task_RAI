from typing import List

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True


class TokenData(BaseModel):
    username: str | None = None


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class ChatRequest(BaseModel):
    message: str


class MessageRequest(BaseModel):
    text: str


class MessageResponse(BaseModel):
    id: int
    text: str
    sender: str
    timestamp: str


class ChatHistoryResponse(BaseModel):
    chat_id: int
    messages: List[MessageResponse]


class ChatRenameRequest(BaseModel):
    name: str
