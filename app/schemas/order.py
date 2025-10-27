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

class OrderCreate(OrderBase):
    # فیلد `date` به صورت خودکار در مدل مقداردهی می‌شود، پس در ورودی نیاز نیست.
    pass
    drug_ids: List[int]
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

