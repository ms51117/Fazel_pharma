# app/models/message.py

from typing import Optional, TYPE_CHECKING,List
from sqlmodel import Field, Relationship, SQLModel,Column
from app.models.base import BaseDates
from typing import Optional, TYPE_CHECKING, List
from sqlmodel import Field, Relationship, SQLModel, JSON


if TYPE_CHECKING:
    from app.models.user import User
    from app.models.patient import Patient


class MessageBase(SQLModel):
    """Base model for Message shared properties"""
    user_id: Optional[int] = Field(
        foreign_key="tbl_User.user_id",
        nullable=True,
        description="User ID"
    )
    patient_id: Optional[int] = Field(
        foreign_key="tbl_Patient.patient_id",
        nullable=True,
        description="Patient ID"
    )
    messages: Optional[str] = Field(
        max_length=2000,
        nullable=False,
        description="Message content"
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
    attachment_path: Optional[List[str]] = Field(
        sa_column=Column(JSON),
        default=[],
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
    user: "User" = Relationship(back_populates="messages")
    patient: "Patient" = Relationship(back_populates="messages")
