# app/models/payment_list.py

from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel
from datetime import datetime
from decimal import Decimal
from app.models.base import BaseDates
import enum

if TYPE_CHECKING:
    from app.models.order import Order
    from app.models.user import User


class PaymentStatusEnum(str, enum.Enum):
    """Enum for payment status"""
    NOT_SEEN = "Not Seen"
    ACCEPTED = "Accepted"
    REJECTED = "Rejected"

class PaymentListBase(SQLModel):
    """Base model for PaymentList shared properties"""
    order_id: int = Field(
        foreign_key="tbl_Order.order_id",
        nullable=False,
        description="Order ID"
    )
    user_id: Optional [int] = Field(
        foreign_key="tbl_User.user_id",
        default=None,
        nullable=True,
        description="User ID who approve the payment ( casher)"
    )
    payment_date: datetime = Field(
        default_factory=datetime.now,
        nullable=False,
        description="Payment date"
    )
    payment_refer_code: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Payment reference code"
    )
    payment_path_file: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Path to payment receipt file"
    )
    payment_value: Decimal = Field(
        max_digits=12,
        decimal_places=0,
        nullable=False,
        description="Payment amount in Rials"
    )
    payment_status: Optional[PaymentStatusEnum] = Field(
        default=PaymentStatusEnum.NOT_SEEN,
        nullable=False,
        description="Payment status"
    )
    payment_status_explain: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Explanation for payment status"
    )


class PaymentList(PaymentListBase, BaseDates, table=True):
    """Database model for PaymentList table (tbl_PaymentList)"""
    __tablename__ = "tbl_PaymentList"

    payment_list_id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Auto-incremented payment list ID"
    )

    # Relationships
    order: "Order" = Relationship(back_populates="payment_list")
    user: "User" = Relationship(back_populates="payment_list")


