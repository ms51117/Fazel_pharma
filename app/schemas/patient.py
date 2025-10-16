# app/schemas/patient.py

from typing import Optional
from sqlmodel import SQLModel
from datetime import datetime
from app.models.patient import PatientBase,GenderEnum # مدل پایه را برای استفاده مجدد وارد می‌کنیم

# ------------------- CREATE SCHEMA -------------------
# این اسکیما دقیقاً همان PatientBase است.
# کاربر تمام فیلدهای پایه را برای ایجاد یک بیمار جدید ارائه می‌دهد.


class PatientCreate(PatientBase):
    pass # هیچ فیلد اضافی لازم نیست

# ------------------- READ SCHEMA -------------------
# این اسکیما برای نمایش اطلاعات بیمار به کاربر است.
# علاوه بر فیلدهای پایه، شامل شناسه و تاریخ‌ها هم می‌شود.
class PatientRead(PatientBase):
    patient_id: int
    created_at: datetime
    updated_at: datetime

# ------------------- UPDATE SCHEMA -------------------
# این اسکیما برای به‌روزرسانی اطلاعات یک بیمار موجود است.
# همه فیلدها Optional هستند تا کاربر مجبور نباشد همه چیز را ارسال کند.
class PatientUpdate(SQLModel):
    full_name: Optional[str] = None
    sex: Optional[GenderEnum] = None
    age: Optional[int] = None
    weight: Optional[float] = None
    height: Optional[float] = None
    mobile_number: Optional[str] = None
    postal_code: Optional[str] = None
    address: Optional[str] = None
    telegram_id: Optional[str] = None
    specific_diseases: Optional[str] = None
    special_conditions: Optional[str] = None
    consultant_type: Optional[str] = None
