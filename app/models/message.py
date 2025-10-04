# app/models/message.py

from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel
from app.models.base import BaseDates

if TYPE_CHECKING:
    from app.models.user import User


class MessageBase(SQLModel):
    """Base model for Message shared properties"""
    user_id: int = Field(
        # foreign_key="tbl_user.user_id",
        nullable=False,
        description="User ID"
    )
    telegram_id: str = Field(
        max_length=100,
        nullable=False,
        description="Telegram ID of sender/receiver"
    )
    messages: str = Field(
        max_length=2000,
        nullable=False,
        description="Message content"
    )
    attachment_path: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Path to attachment file (voice, image, etc.)"
    )


class Message(MessageBase, BaseDates, table=True):
    """Database model for Message table (tbl_message)"""
    __tablename__ = "tbl_Message"

    messages_id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Auto-incremented message ID"
    )

    # Relationships
    # user: "User" = Relationship(back_populates="messages")
