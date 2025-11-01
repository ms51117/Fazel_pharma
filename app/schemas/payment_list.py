# app/schemas/payment_list_schema.py
from decimal import Decimal
from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime

from app.core.enums import PaymentStatusEnum
from app.models.payment_list import PaymentListBase

# ---------------------------------------------------------------------------
# 1. اسکیمای پایه و ورودی برای ایجاد پرداخت (CREATE)
# ---------------------------------------------------------------------------
# این اسکیما شامل تمام فیلدهایی است که هنگام ایجاد یک رکورد پرداخت جدید نیاز داریم.

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
    payment_date : datetime = None
    payment_refer_code : Optional[str] = None
    payment_path_file: Optional[str] = None
    payment_value: Decimal = None
    payment_status: PaymentStatusEnum = None
    payment_status_explain : Optional[str] = None

