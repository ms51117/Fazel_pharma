# app/models/bot_message.py

from typing import Optional
from sqlmodel import Field, SQLModel
from app.models.base import BaseDates

class BotMessageBase(SQLModel):
    """Base model for BotMessage shared properties"""
    message_key: str = Field(
        max_length=100,
        unique=True,
        index=True,
        nullable=False,
        description="The unique key used in code to fetch this message (e.g., 'welcome_start')"
    )
    message_text: str = Field(
        nullable=False,
        description="The content of the message sent to user"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Internal note for admin to know what this message is for"
    )

class BotMessage(BotMessageBase, BaseDates, table=True):
    """Database model for storing static bot strings (tbl_BotMessage)"""
    __tablename__ = "tbl_BotMessage"

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Auto-incremented ID"
    )

    def __str__(self) -> str:
        return f"{self.description} ({self.message_key})"
