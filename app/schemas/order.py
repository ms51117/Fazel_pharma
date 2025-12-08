# app/schemas/order_schema.py
import enum
from typing import Optional, List
from sqlmodel import SQLModel, Field
from datetime import datetime

# این اسکیماها بعدا در OrderRead استفاده خواهند شد.
# فعلا تعریف ساده‌ای از آنها داریم.
from app.schemas.order_list import OrderListRead
from app.schemas.payment_list import PaymentListRead
from app.models.order import OrderBase,OrderStatusEnum

# ---------------------------------------------------------------------------
# 1. اسکیمای پایه و ورودی برای ایجاد سفارش (CREATE)
# ---------------------------------------------------------------------------
class OrderItemInput(SQLModel):
    drug_id: int
    qty: int = 1  # پیش‌فرض 1 باشد

class OrderCreate(OrderBase):
    # فیلد `date` به صورت خودکار در مدل مقداردهی می‌شود، پس در ورودی نیاز نیست.
    pass
    items: List[OrderItemInput]

    order_status: Optional[OrderStatusEnum] = None

# ---------------------------------------------------------------------------
# 2. اسکیمای ورودی برای آپدیت سفارش (UPDATE)
# ---------------------------------------------------------------------------
class OrderUpdate(SQLModel):
    # معمولا فقط وضعیت سفارش آپدیت می‌شود، اما برای انعطاف‌پذیری اینها را هم می‌گذاریم.
    patient_id: Optional[int] = None
    user_id: Optional[int] = None
    order_status: Optional[OrderStatusEnum] = None
    updated_at: datetime = None

    # می‌توان فیلدهای دیگری مثل order_status را در آینده به مدل اضافه و اینجا آپدیت کرد.

# ---------------------------------------------------------------------------
# 3. اسکیمای خروجی برای نمایش اطلاعات سفارش (READ)
# ---------------------------------------------------------------------------
# این اسکیما فقط اطلاعات خود سفارش را برمی‌گرداند.
class OrderRead(OrderBase):
    order_id: int
    created_at: datetime
    updated_at: datetime

# ---------------------------------------------------------------------------
# 4. اسکیمای خروجی کامل همراه با روابط (اقلام و پرداخت‌ها)
# ---------------------------------------------------------------------------
# این اسکیما برای خواندن یک سفارش به همراه تمام جزئیاتش (Lazy/Eager Loading) استفاده می‌شود.
# فعلا به دلیل اینکه اسکیماهای OrderList و PaymentList کامل نیستند، آن را کامنت می‌کنیم.
# بعد از ساخت OrderList آن را تکمیل خواهیم کرد.

class OrderReadWithDetails(OrderRead):
    order_list: List[OrderListRead] = []
    payment_list: List[PaymentListRead] = []


# --------------------------------------------------
class OrderItemUpdate(SQLModel):
    """
    Represents a single item in the order update request.
    Client only needs to send drug_id and quantity.
    Price will be fetched from the database for security.
    """
    drug_id: int
    qty: int = Field(default=1, gt=0, description="Quantity must be greater than zero")


# --- اسکیمای جامع و جدید برای آپدیت سفارش ---
class OrderComprehensiveUpdate(SQLModel):
    """
    A comprehensive schema for updating an order.
    All fields are optional, so the client can update only what's needed.
    """
    order_status: Optional[OrderStatusEnum] = None
    order_items: Optional[List[OrderItemUpdate]] = Field(
        default=None,
        description="If provided, replaces the ENTIRE existing list of items."
    )
