# app/models/api_client.py

from typing import Optional
from sqlmodel import Field, SQLModel
from app.models.base import BaseDates
import secrets


class ApiClientBase(SQLModel):
    """
    Base model for API client properties.
    """
    client_name: str = Field(
        unique=True,
        index=True,
        nullable=False,
        max_length=50,
        description="A unique name for the client (e.g., 'telegram-bot')"
    )
    is_active: bool = Field(
        default=True,
        description="Whether this API key is currently active and can be used."
    )


class ApiClient(ApiClientBase, BaseDates, table=True):
    """
    Database model for API clients and their keys.
    """
    __tablename__ = "tbl_ApiClient"

    id: Optional[int] = Field(default=None, primary_key=True)

    # The API key itself. Should be long and random.
    api_key: str = Field(
        unique=True,
        index=True,
        nullable=False,
        max_length=128,
        description="The actual API key for authentication."
    )

    # Hashed version of the key for secure storage and verification.
    hashed_api_key: str = Field(
        unique=True,
        index=True,
        nullable=False,
        max_length=255,
        description="Hashed version of the API key for secure comparison."
    )
