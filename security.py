# /security.py

from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt
from passlib.context import CryptContext
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from setting import settings
from database import get_session
from app.models.user import User
from app.schemas.token import TokenPayload

# Context برای هش کردن و بررسی رمز عبور
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# این اسکما فقط برای این است که به Swagger بگوییم اندپوینت لاگین کجاست
# و باعث می‌شود در اندپوینت /login فرم username/password نمایش داده شود.
# ما از این اسکما برای محافظت از روت‌های دیگر استفاده *نخواهیم* کرد.
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"/api/v1/login/access-token"
)

# این اسکیمای امنیتی اصلی ما برای محافظت از اندپوینت‌ها است.
# این اسکیم به Swagger می‌گوید که فقط یک فیلد برای وارد کردن "Bearer Token" نمایش بده.
bearer_scheme = HTTPBearer()

ALGORITHM = "HS256"


def create_access_token(subject: str | Any, expires_delta: timedelta | None = None) -> str:
    """
    ایجاد توکن JWT جدید.
    subject: شناسه‌ای که می‌خواهیم داخل توکن قرار دهیم (در اینجا شماره موبایل).
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """بررسی تطابق رمز عبور ساده با نسخه هش شده."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """هش کردن رمز عبور ساده."""
    return pwd_context.hash(password)


async def get_current_user(
        session: AsyncSession = Depends(get_session),
        # وابستگی ما به HTTPBearer است تا Swagger فرم درست را نشان دهد
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> User:
    """
    وابستگی (Dependency) برای دریافت کاربر فعلی از توکن JWT.
    توکن را از هدر استخراج، رمزگشایی و کاربر مربوطه را از دیتابیس پیدا می‌کند.
    """
    # credentials.credentials خود رشته توکن است
    token = credentials.credentials

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # رمزگشایی توکن
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[ALGORITHM]
        )
        # استخراج payload و اعتبارسنجی با اسکیمای TokenPayload
        token_data = TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        # اگر توکن نامعتبر یا منقضی شده باشد، خطا برگردانده می‌شود
        raise credentials_exception

    # استخراج شماره موبایل از فیلد 'sub' توکن
    mobile_number = token_data.sub

    # جستجوی کاربر در دیتابیس با استفاده از شماره موبایل
    query = select(User).where(User.mobile_number == mobile_number)
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if user is None:
        # اگر کاربری با این شماره موبایل پیدا نشد
        raise credentials_exception

    return user


async def get_current_active_user(
        current_user: User = Depends(get_current_user),
) -> User:
    """
    وابستگی برای بررسی فعال بودن کاربر فعلی.
    ابتدا get_current_user را اجرا می‌کند و سپس فیلد is_active را چک می‌کند.
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
