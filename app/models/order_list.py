# app/models/order_list.py

from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel
from decimal import Decimal
from app.models.base import BaseDates

if TYPE_CHECKING:
    from app.models.order import Order
    from app.models.drug import Drug


class OrderListBase(SQLModel):
    """Base model for OrderList shared properties"""
    order_id: int = Field(
        # foreign_key="tbl_Order.order_id",
        nullable=False,
        description="Order ID"
    )
    drug_id: int = Field(
        # foreign_key="tbl_drug.drugs_id",
        nullable=False,
        description="Drug ID"
    )
    qty: int = Field(
        nullable=False,
        description="Quantity"
    )
    price: Decimal = Field(
        max_digits=12,
        decimal_places=0,
        nullable=False,
        description="Price per unit"
    )


class OrderList(OrderListBase, BaseDates, table=True):
    """Database model for OrderList table (tbl_OrderList)"""
    __tablename__ = "tbl_OrderList"

    order_list_id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Auto-incremented order list ID"
    )

    # Relationships
    # order: "Order" = Relationship(back_populates="order_lists")
    # drug: "Drug" = Relationship(back_populates="order_lists")
