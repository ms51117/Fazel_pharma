# app/models/payment_list.py

from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel
from datetime import datetime
from decimal import Decimal
from app.models.base import BaseDates

if TYPE_CHECKING:
    from app.models.order import Order
    from app.models.user import User


class PaymentListBase(SQLModel):
    """Base model for PaymentList shared properties"""
    order_id: int = Field(
        # foreign_key="tbl_Order.order_id",
        nullable=False,
        description="Order ID"
    )
    user_id: int = Field(
        # foreign_key="tbl_user.user_id",
        nullable=False,
        description="User ID who made the payment"
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
    payment_status: int = Field(
        default=0,
        nullable=False,
        description="Payment status: 0=NotSeen, 1=Accepted, 2=Rejected"
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
    # order: "Order" = Relationship(back_populates="payment_lists")
    # user: "User" = Relationship(back_populates="payment_lists")



    # ---------------------------------------------------schemas---------------------------------



    # Helper property to get payment status text
#     @property
#     def payment_status_text(self) -> str:
#         """Return human-readable payment status"""
#         status_map = {
#             0: "NotSeen",
#             1: "Accepted",
#             2: "Rejected"
#         }
#         return status_map.get(self.payment_status, "Unknown")
#
#
# class PaymentListCreate(PaymentListBase):
#     """Schema for creating a new payment"""
#     pass
#
#
# class PaymentListRead(PaymentListBase):
#     """Schema for reading payment data"""
#     payment_list_id: int
#     created_at: datetime
#     updated_at: Optional[datetime]
#
#     class Config:
#         from_attributes = True
#
#
# class PaymentListUpdate(SQLModel):
#     """Schema for updating payment data"""
#     payment_refer_code: Optional[str] = None
#     payment_path_file: Optional[str] = None
#     payment_value: Optional[Decimal] = None
#     payment_status: Optional[int] = None
#     payment_status_explain: Optional[str] = None
