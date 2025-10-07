# app/models/message.py

from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel
from app.models.base import BaseDates

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.patient import Patient


class MessageBase(SQLModel):
    """Base model for Message shared properties"""
    user_id: int = Field(
        foreign_key="tbl_User.user_id",
        nullable=True,
        description="User ID"
    )
    patient_id: int = Field(
        foreign_key="tbl_Patient.patient_id",
        nullable=True,
        description="Patient ID"
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
    messages_seen: Optional[bool] = Field(
        default=False,
        nullable=False,
        description="Seen messages , if seen == T if not seen == F"
    )
    messages_sender: Optional[bool] = Field(
        nullable=False,
        description="messages sender , if sender == patient then T if sender == user then F"
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
    user: "User" = Relationship(back_populates="messages")
    patient: "Patient" = Relationship(back_populates="messages")
