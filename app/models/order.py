# app/models/order.py

from typing import Optional, TYPE_CHECKING, List
from sqlmodel import Field, Relationship, SQLModel
from datetime import datetime
from app.models.base import BaseDates

if TYPE_CHECKING:
    from app.models.patient import Patient
    from app.models.user import User
    from app.models.order_list import OrderList
    from app.models.payment_list import PaymentList


class OrderBase(SQLModel):
    """Base model for Order shared properties"""
    date: datetime = Field(
        default_factory=datetime.now,
        nullable=False,
        description="Order date"
    )
    patient_id: int = Field(
        foreign_key="tbl_Patient.patient_id",
        nullable=False,
        description="Patient ID"
    )
    user_id: int = Field(
        # foreign_key="tbl_user.user_id",
        nullable=False,
        description="User ID who created the order"
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
    # patient: "Patient" = Relationship(back_populates="orders")
    # user: "User" = Relationship(back_populates="orders")
    # order_lists: List["OrderList"] = Relationship(back_populates="order")
    # payment_lists: List["PaymentList"] = Relationship(back_populates="order")
