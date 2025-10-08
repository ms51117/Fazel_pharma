# app/routes/login.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Any

from database import get_session
from app.models.user import User
from app.schemas.token import Token, LoginRequest  # ما از LoginRequest که ساختیم استفاده می‌کنیم
from security import create_access_token, verify_password

# یک روتر جدید برای مسیرهای مربوط به احراز هویت ایجاد می‌کنیم
router = APIRouter()


@router.post("/access-token", response_model=Token)
async def login_for_access_token(
        *,
        session: AsyncSession = Depends(get_session),
        # ما از اسکیمای LoginRequest خودمان استفاده می‌کنیم تا ورودی را از بدنه JSON بگیریم
        form_data: LoginRequest
) -> Any:
    """
    این اندپوینت برای لاگین کاربر و دریافت توکن دسترسی استفاده می‌شود.
    ورودی آن یک JSON با فیلدهای 'username' (که همان شماره موبایل است) و 'password' می‌باشد.
    """

    # 1. جستجوی کاربر در دیتابیس بر اساس شماره موبایل
    # فیلد ورودی ما 'username' نام دارد اما ما آن را برای جستجوی 'mobile_number' استفاده می‌کنیم
    statement = select(User).where(User.mobile_number == form_data.username)
    db_user = (await session.exec(statement)).one_or_none()

    # 2. بررسی اینکه آیا کاربر وجود دارد و رمز عبور صحیح است یا خیر
    # برای امنیت بیشتر، یک پیام خطا برای هر دو حالت (کاربر ناموجود یا رمز اشتباه) برمی‌گردانیم
    # تا مهاجم نتواند بفهمد کدام یک اشتباه بوده است.
    if not db_user or not verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect mobile number or password",
        )

    # 3. بررسی اینکه آیا کاربر فعال است یا خیر
    if not db_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")

    # 4. ایجاد توکن دسترسی
    # همانطور که شما خواستید، شماره موبایل کاربر را به عنوان 'subject' در توکن قرار می‌دهیم
    access_token = create_access_token(
        subject=db_user.mobile_number
    )

    # 5. برگرداندن توکن در قالب اسکیمای Token
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }
