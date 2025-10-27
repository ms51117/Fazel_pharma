# app/schemas/patient.py

from typing import Optional, List
from sqlmodel import SQLModel
from datetime import datetime,date
from app.models.patient import PatientBase,GenderEnum,PatientStatus # مدل پایه را برای استفاده مجدد وارد می‌کنیم

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
    patient_status : PatientStatus
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
    patient_status: Optional[PatientStatus] = None
    updated_at: Optional[datetime] = None


class WaitingForConsultantDatesResponse(SQLModel):
    dates: Optional[List[date]] = None



class AwaitingForConsultationPatientInfo(SQLModel): # یا BaseModel
    """Schema برای اطلاعات یک بیمار با پیام خوانده نشده"""
    telegram_id: Optional[str] = None
    full_name: Optional[str] = None

class AwaitingForConsultationPatientsResponse(SQLModel): # یا BaseModel
    """Schema برای لیست بیماران با پیام خوانده نشده"""
    patients: Optional[List[AwaitingForConsultationPatientInfo]] = None