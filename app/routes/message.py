# app/routes/message.py

from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select,func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import Date
from datetime import date


from app.core.permission import FormName, PermissionAction, RoleChecker
from database import get_session
from app.models.message import Message
from app.models.patient import Patient  # برای اعتبارسنجی
from app.schemas.message import MessageCreate, MessageRead, MessageUpdate, MessageReadWithDetails, UnreadDatesResponse, \
    UnreadPatientsResponse
from security import get_current_active_user
from app.models.user import User

router = APIRouter()


async def get_patient_or_404(patient_id: int, session: AsyncSession):
    """Helper function to check if Patient exists."""
    patient = await session.get(Patient, patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {patient_id} not found."
        )
    return patient


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=MessageRead)
async def create_message(
        *,
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_session),
        _permission_check: None = Depends(
            RoleChecker(form_name=FormName.MESSAGE, required_permission=PermissionAction.INSERT)),
        message_in: MessageCreate,
) -> Any:
    """
    ایجاد یک پیام جدید برای یک بیمار.
    """
    # 1. اعتبارسنجی وجود `patient_id`
    await get_patient_or_404(message_in.patient_id, session)

    # 2. ایجاد آبجکت پیام و ذخیره
    # فیلد message_date به طور خودکار توسط دیتابیس (default=func.now()) پر می‌شود
    db_message = Message.model_validate(message_in)
    session.add(db_message)
    await session.commit()
    await session.refresh(db_message)
    return db_message


@router.get("/", response_model=List[MessageRead])
async def read_messages(
        *,
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_session),
        _permission_check: None = Depends(
            RoleChecker(form_name=FormName.MESSAGE, required_permission=PermissionAction.VIEW)),
        skip: int = 0,
        limit: int = 100,
) -> Any:
    """
    دریافت لیست پیام‌ها همراه با اطلاعات بیمار.
    """
    statement = select(Message).order_by(Message.created_at.desc()).offset(
        skip).limit(limit)
    messages = (await session.exec(statement)).all()
    return messages


@router.get("/{message_id}", response_model=MessageRead)
async def read_message_by_id(
        *,
        current_user: User = Depends(get_current_active_user),
        _permission_check: None = Depends(
            RoleChecker(form_name=FormName.MESSAGE, required_permission=PermissionAction.VIEW)),
        message_id: int,
        session: AsyncSession = Depends(get_session),
) -> Any:
    """
    دریافت اطلاعات یک پیام با شناسه (ID) به همراه اطلاعات بیمار.
    """
    statement = select(Message).where(Message.message_id == message_id).order_by(Message.created_at.desc())
    message = (await session.exec(statement)).one_or_none()

    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Message with ID {message_id} not found",
        )
    return message


@router.patch("/{message_id}", response_model=MessageRead)
async def update_message(
        *,
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_session),
        _permission_check: None = Depends(
            RoleChecker(form_name=FormName.MESSAGE, required_permission=PermissionAction.UPDATE)),
        message_id: int,
        message_in: MessageUpdate,
) -> Any:
    """
    آپدیت متن یک پیام.
    """
    db_message = await session.get(Message, message_id)
    if not db_message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Message with ID {message_id} not found",
        )

    update_data = message_in.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No data to update")

    db_message.sqlmodel_update(update_data)
    session.add(db_message)
    await session.commit()
    await session.refresh(db_message)
    return db_message


@router.delete("/{message_id}")
async def delete_message(
        *,
        current_user: User = Depends(get_current_active_user),
        _permission_check: None = Depends(
            RoleChecker(form_name=FormName.MESSAGE, required_permission=PermissionAction.DELETE)),
        message_id: int,
        session: AsyncSession = Depends(get_session),
):
    """
    حذف یک پیام.
    """
    message = await session.get(Message, message_id)
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Message with ID {message_id} not found",
        )

    await session.delete(message)
    await session.commit()
    return {"ok": True, "message": "Message deleted successfully"}


@router.get("/unread-message-dates/", response_model=UnreadDatesResponse)
async def get_unread_message_dates(
        *,
        current_user: User = Depends(get_current_active_user),
        _permission_check: None = Depends(
            RoleChecker(form_name=FormName.MESSAGE, required_permission=PermissionAction.VIEW)),
        session: AsyncSession = Depends(get_session),
) -> Any:
    """
برای دریافت تاریخ هایی که در ان پیام نخانده شده وجود دارد
    """
    statement = (
        select(func.cast(Message.created_at, Date))
        .where(Message.messages_seen == False)
        .distinct()
        .order_by(func.cast(Message.created_at, Date).desc())
    )
    results = await session.exec(statement)

    # 3. دریافت تمام نتایج به صورت یک لیست
    #    .all() در اینجا لیستی از تاریخ‌ها را برمی‌گرداند
    unread_dates = results.all()

    # 4. برگرداندن نتیجه در قالب schema تعریف شده
    return UnreadDatesResponse(dates=unread_dates)

@router.get("/history/{patient_id}", response_model=List[MessageRead])
async def read_history_by_id(
        *,
        current_user: User = Depends(get_current_active_user),
        _permission_check: None = Depends(
            RoleChecker(form_name=FormName.MESSAGE, required_permission=PermissionAction.VIEW)),
        patient_id: int,
        session: AsyncSession = Depends(get_session),
) -> Any:
    """
    دریافت اطلاعات یک پیام با شناسه (ID) به همراه اطلاعات بیمار.
    """
    statement = select(Message).where(Message.patient_id == patient_id).order_by(Message.created_at.asc())
    message = await session.exec(statement)
    response = message.all()


    if not response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Message for patient with ID {patient_id} not found",
        )
    return response

