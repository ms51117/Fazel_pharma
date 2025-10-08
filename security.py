# app/core/security.py

from datetime import datetime, timedelta, timezone
from typing import Any, Union

import jwt
from passlib.context import CryptContext

# وارد کردن تنظیمات از فایل config
from setting import settings

# این بخش از قبل وجود داشت

ALGORITHM = settings.ALGORITHM
SECRET_KEY = settings.SECRET_KEY





# Create a CryptContext instance for password hashing.
# We specify "bcrypt" as the hashing scheme.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain password against a hashed password.

    :param plain_password: The password in plain text.
    :param hashed_password: The hashed password from the database.
    :return: True if passwords match, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Hashes a plain password using bcrypt.

    :param password: The password in plain text.
    :return: The hashed password.
    """
    return pwd_context.hash(password)


def create_access_token(
        subject: Union[str, Any], expires_delta: timedelta = None
) -> str:
    """
    این تابع یک توکن دسترسی JWT جدید ایجاد می‌کند.

    Args:
        subject: داده‌ای که می‌خواهیم درون توکن ذخیره کنیم (معمولاً شناسه یا نام کاربری کاربر).
        expires_delta: مدت زمان اعتبار توکن. اگر مشخص نشود، از مقدار پیش‌فرض استفاده می‌کند.

    Returns:
        یک رشته که همان توکن امضا شده است.
    """
    # تعیین زمان انقضای توکن
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # اگر زمان انقضا داده نشده بود، از تنظیمات برنامه (مثلاً 60 دقیقه) استفاده کن
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    # داده‌هایی که باید در توکن (payload) قرار گیرند
    to_encode = {"exp": expire, "sub": str(subject)}

    # ساخت (encode) و امضای توکن با استفاده از کلید مخفی و الگوریتم مشخص شده
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt