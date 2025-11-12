
# app/models/user.py

from typing import Optional, TYPE_CHECKING, List

from sqlalchemy.orm import relationship
from sqlmodel import Field, Relationship, SQLModel
from datetime import datetime
from app.models.base import BaseDates

# Prevent circular imports
if TYPE_CHECKING:
    from app.models.user_role import UserRole
    from app.models.payment_list import PaymentList
    from app.models.order import Order
    from app.models.patient import Patient
    from app.models.message import Message


class UserBase(SQLModel):
    """
    Base model for User shared properties.
    Used for request/response schemas.
    """
    # Telegram specific
    telegram_id: str = Field(
        index=True,
        unique=True,
        nullable=False,
        max_length=100,
        description="Unique Telegram ID for bot integration"
    )

    # Personal information
    full_name: str = Field(
        max_length=100,
        nullable=False,
        description="User's full name"
    )
    national_code: Optional[str] = Field(
        default=None,
        unique=True,
        max_length=10,
        regex="^[0-9]{10}$",  # Validation for 10 digits
        description="10-digit Iranian national code"
    )
    mobile_number: Optional[str] = Field(
        default=None,
        unique=True,
        max_length=11,
        regex="^09[0-9]{9}$",  # Iranian mobile format
        description="Mobile number (09XXXXXXXXX)"
    )
    address: Optional[str] = Field(
        default=None,
        max_length=500,  # Increased for full addresses
        description="User's physical address"
    )

    # Account status
    is_active: bool = Field(
        default=True,
        description="Whether the account is active"
    )
    is_verified: bool = Field(
        default=False,
        description="Whether phone number is verified"
    )


class User(UserBase, BaseDates, table=True):
    """
    Database model for the User table (tbl_user).
    Represents consultants, admins, and accountants.
    """
    __tablename__ = "tbl_User"

    # Primary key
    user_id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Auto-incremented user ID"
    )

    # Security (not in UserBase for security reasons)
    hashed_password: str = Field(
        nullable=False,
        max_length=255,
        exclude=True,  # Exclude from API responses by default
        description="Bcrypt hashed password"
    )

    # Authentication tracking
    last_login: Optional[datetime] = Field(
        default=None,
        description="Last successful login timestamp"
    )
    login_attempts: int = Field(
        default=0,
        description="Failed login attempts counter"
    )

    # Foreign Key to UserRole (removed from base)
    role_id: Optional[int] = Field(
        default=None,
        foreign_key="tbl_UserRole.role_id",
        description="Reference to user's role"
    )

    # # Relationships
    role: "UserRole" = Relationship(back_populates="user")
    payment_list : Optional["PaymentList"]=Relationship(back_populates="user")
    order: Optional["Order"]=Relationship(back_populates="user")
    messages: Optional["Message"] = Relationship(back_populates="user")

    def __str__(self) -> str:
        """
        این متد به پایتون و sqladmin می‌گوید که هرگاه خواستید یک نمونه
        از این کلاس را به صورت رشته نمایش دهید، فقط مقدار role_name را برگردانید.
        """
        return self.full_name



