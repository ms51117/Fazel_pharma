# app/models/order.py

from typing import Optional, TYPE_CHECKING, List
from sqlmodel import Field, Relationship, SQLModel
from datetime import datetime
from app.models.base import BaseDates
import enum


if TYPE_CHECKING:
    from app.models.patient import Patient
    from app.models.user import User
    from app.models.order_list import OrderList
    from app.models.payment_list import PaymentList

class OrderStatusEnum(str, enum.Enum):
    """Enum for payment status"""
    CREATED = "Created"
    CONFIRM = "Confirm"
    REJECTED = "Rejected"
    PAID = "Paid"
    SENT = "Sent"
    DELIVERED = "Delived"




class OrderBase(SQLModel):
    """Base model for Order shared properties"""

    patient_id: int = Field(
        foreign_key="tbl_Patient.patient_id",
        nullable=False,
        description="Patient ID"
    )
    user_id: int = Field(
        foreign_key="tbl_User.user_id",
        nullable=False,
        description="User ID who created the order"
    )
    order_status: OrderStatusEnum = Field(
        default=OrderStatusEnum.CREATED,
        nullable=False,
        description="Order Status"
    )


class Order(OrderBase, BaseDates, table=True):
    """Database model for Order table (tbl_Order)"""
    __tablename__ = "tbl_Order"

    order_id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Auto-incremented order ID"
    )

    # Relationships
    patient: "Patient" = Relationship(back_populates="order")
    user: "User" = Relationship(back_populates="order")
    order_list: Optional["OrderList"] = Relationship(back_populates="order")
    payment_list: Optional["PaymentList"] = Relationship(back_populates="order")
