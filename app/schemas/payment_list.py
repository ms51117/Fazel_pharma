# app/schemas/payment_list_schema.py

from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime

# ---------------------------------------------------------------------------
# 1. اسکیمای پایه و ورودی برای ایجاد پرداخت (CREATE)
# ---------------------------------------------------------------------------
# این اسکیما شامل تمام فیلدهایی است که هنگام ایجاد یک رکورد پرداخت جدید نیاز داریم.
class PaymentListBase(SQLModel):
    user_id: int = Field(description="ID of the user making the payment", foreign_key="tbl_User.user_id")
    amount: float = Field(description="Payment amount")
    payment_type: str = Field(max_length=50, description="Type of payment (e.g., 'ZarinPal', 'IDPay', 'Card')")
    description: Optional[str] = Field(default=None, max_length=500, description="Optional description for the payment")
    ref_id: Optional[str] = Field(default=None, max_length=100, description="Reference ID from the payment gateway")
    card_number: Optional[str] = Field(default=None, max_length=20, description="Card number used for payment")

class PaymentListCreate(PaymentListBase):
    # این اسکیما برای ورودی POST استفاده می‌شود و در حال حاضر فیلد اضافی ندارد.
    pass

# ---------------------------------------------------------------------------
# 2. اسکیمای خروجی برای نمایش اطلاعات پرداخت (READ)
# ---------------------------------------------------------------------------
# این اسکیما علاوه بر فیلدهای پایه، فیلدهای خودکار دیتابیس را هم نمایش می‌دهد.
class PaymentListRead(PaymentListBase):
    payment_id: int
    payment_date: datetime # این فیلد در مدل شما توسط BaseDates مدیریت می‌شود

# ---------------------------------------------------------------------------
# 3. اسکیمای ورودی برای آپدیت پرداخت (UPDATE)
# ---------------------------------------------------------------------------
# تمام فیلدها اختیاری هستند. توجه کنید که معمولاً user_id و amount آپدیت نمی‌شوند،
# اما برای انعطاف‌پذیری بیشتر اینجا قرار داده شده‌اند.
class PaymentListUpdate(SQLModel):
    user_id: Optional[int] = None
    amount: Optional[float] = None
    payment_type: Optional[str] = None
    description: Optional[str] = None
    ref_id: Optional[str] = None
    card_number: Optional[str] = None
