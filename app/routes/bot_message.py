# app/routes/bot_message.py

from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

# ایمپورت‌های پروژه شما
from app.core.permission import FormName, PermissionAction, RoleChecker
from database import get_session
from app.models.bot_message import BotMessage
from app.schemas.bot_message import BotMessageCreate, BotMessageRead, BotMessageUpdate
from security import get_current_active_user
from app.models.user import User

router = APIRouter()


# ==============================================================================
# 1. روت عمومی مخصوص ربات (بدون نیاز به پرمیشن سخت‌گیرانه)
# ==============================================================================
@router.get("/key/{key}", response_model=BotMessageRead)
async def read_message_by_key(
        key: str,
        session: AsyncSession = Depends(get_session),
        # اینجا RoleChecker را حذف کردیم تا ربات بتواند آزادانه متن را بخواند.
        # اگر می‌خواهید امنیت داشته باشد، می‌توانید یک هدر API_KEY ساده چک کنید.
) -> Any:
    """
    دریافت متن پیام بر اساس کلید (مخصوص استفاده در ربات).
    """
    statement = select(BotMessage).where(BotMessage.message_key == key)
    result = await session.exec(statement)
    bot_message = result.first()

    if not bot_message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Message with key '{key}' not found",
        )
    return bot_message


# ==============================================================================
# 2. روت‌های مدیریتی (CRUD) - مشابه disease_type.py
# ==============================================================================

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=BotMessageRead)
async def create_bot_message(
        *,
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_session),
        # فرض بر اینکه FormName.BOT_MESSAGE را دارید، اگر نه، این خط را کامنت کنید یا اضافه کنید
        # _permission_check: None = Depends(
        #    RoleChecker(form_name="bot_message", required_permission=PermissionAction.INSERT)),
        bot_message_in: BotMessageCreate,
) -> Any:
    """
    ایجاد یک پیام جدید (توسط ادمین).
    """
    db_message = BotMessage.model_validate(bot_message_in)
    session.add(db_message)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Message key already exists.",
        )
    await session.refresh(db_message)
    return db_message


@router.get("/", response_model=List[BotMessageRead])
async def read_all_messages(
        *,
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_session),
        skip: int = 0,
        limit: int = 100,
) -> Any:
    """
    لیست تمام پیام‌ها برای مدیریت.
    """
    statement = select(BotMessage).offset(skip).limit(limit)
    messages = (await session.exec(statement)).all()
    return messages


@router.patch("/{message_id}", response_model=BotMessageRead)
async def update_bot_message(
        *,
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_session),
        message_id: int,
        message_in: BotMessageUpdate,
) -> Any:
    """
    ویرایش متن پیام.
    """
    db_message = await session.get(BotMessage, message_id)
    if not db_message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found",
        )

    update_data = message_in.model_dump(exclude_unset=True)
    db_message.sqlmodel_update(update_data)

    session.add(db_message)
    await session.commit()
    await session.refresh(db_message)
    return db_message
