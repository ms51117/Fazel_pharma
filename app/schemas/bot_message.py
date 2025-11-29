# app/schemas/bot_message.py

from typing import Optional
from sqlmodel import SQLModel
from app.models.bot_message import BotMessageBase

# برای ساختن (Create)
class BotMessageCreate(BotMessageBase):
    pass

# برای آپدیت (Update) - فیلدها اختیاری هستند
class BotMessageUpdate(SQLModel):
    message_key: Optional[str] = None
    message_text: Optional[str] = None
    description: Optional[str] = None

# برای خواندن (Read) - شامل ID هم می‌شود
class BotMessageRead(BotMessageBase):
    id: int
