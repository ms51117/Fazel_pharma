# app/schemas/order_list_schema.py

from typing import Optional
from sqlmodel import SQLModel, Field
from decimal import Decimal

# ---------------------------------------------------------------------------
# 1. اسکیمای پایه و ورودی برای ایجاد قلم سفارش (CREATE)
# ---------------------------------------------------------------------------
class OrderListBase(SQLModel):
    order_id: int = Field(description="ID of the order this item belongs to", foreign_key="tbl_Order.order_id")
    drug_id: int = Field(description="ID of the drug in this order item", foreign_key="tbl_Drug.drugs_id")
    qty: int = Field(description="Quantity of the drug")
    price: Decimal = Field(max_digits=12, decimal_places=0, description="Price per unit at the time of order")

class OrderListCreate(OrderListBase):
    pass

# ---------------------------------------------------------------------------
# 2. اسکیمای ورودی برای آپدیت قلم سفارش (UPDATE)
# ---------------------------------------------------------------------------
class OrderListUpdate(SQLModel):
    # معمولاً فقط تعداد (qty) یا قیمت (price) آپدیت می‌شود.
    # تغییر order_id یا drug_id منطقی نیست و بهتر است حذف و دوباره ایجاد شود.
    qty: Optional[int] = None
    price: Optional[Decimal] = None
    order_id: Optional[int] = None
    drug_id: Optional[int] = None


# ---------------------------------------------------------------------------
# 3. اسکیمای خروجی برای نمایش اطلاعات قلم سفارش (READ)
# ---------------------------------------------------------------------------
class OrderListRead(OrderListBase):
    order_list_id: int

# ---------------------------------------------------------------------------
# 4. اسکیمای خروجی با جزئیات (مثلاً نام دارو)
# ---------------------------------------------------------------------------
# این اسکیما بعد از پیاده‌سازی مدل Drug تکمیل خواهد شد.
# from app.schemas.drug_schema import DrugRead
#
# class OrderListReadWithDetails(OrderListRead):
#     drug: Optional[DrugRead] = None
