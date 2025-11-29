# app/schemas/message_schema.py

from typing import Optional,List
from sqlmodel import SQLModel, Field
from datetime import datetime, date

# برای نمایش اطلاعات بیمار در خروجی پیام
from app.schemas.patient import PatientRead
from app.models.message import MessageBase




# ---------------------------------------------------------------------------
# 2. اسکیمای ایجاد (Create)
# ---------------------------------------------------------------------------
class MessageCreate(MessageBase):
    pass


# ---------------------------------------------------------------------------
# 3. اسکیمای آپدیت (Update)
# ---------------------------------------------------------------------------
class MessageUpdate(SQLModel):
    message_text: Optional[str] = None
    # معمولا patient_id یک پیام را تغییر نمی‌دهیم، پس اینجا نیست


# ---------------------------------------------------------------------------
# 4. اسکیمای پایه برای خواندن (Read) - بدون روابط
# ---------------------------------------------------------------------------
class MessageRead(MessageBase):
    messages_id: Optional[int] = None

# ---------------------------------------------------------------------------
# 5. اسکیمای کامل برای خواندن (Read) - با جزئیات بیمار
# ---------------------------------------------------------------------------
class MessageReadWithDetails(MessageRead):
    patient: Optional[PatientRead] = None


class UnreadDatesResponse(SQLModel):
    """
    Schema for the response of unread message dates endpoint.
    """
    dates: Optional[List[date]] = None


# -------------------------------------------


class UnreadPatientInfo(SQLModel): # یا BaseModel
    """Schema برای اطلاعات یک بیمار با پیام خوانده نشده"""
    telegram_id: Optional[str] = None
    full_name: Optional[str] = None

class UnreadPatientsResponse(SQLModel): # یا BaseModel
    """Schema برای لیست بیماران با پیام خوانده نشده"""
    patients: Optional[List[UnreadPatientInfo]] = None