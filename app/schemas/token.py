# app/schemas/token.py

from pydantic import BaseModel

class Token(BaseModel):
    """
    اسکیمای خروجی برای توکن.
    این ساختار به فرانت‌اند ارسال می‌شود.
    """
    access_token: str
    token_type: str = "bearer"  # نوع توکن که طبق استاندارد OAuth2 معمولاً "bearer" است

class TokenPayload(BaseModel):
    """
    اسکیمای داخلی برای داده‌های درون توکن (payload).
    این برای اعتبارسنجی محتوای توکن پس از decode کردن آن استفاده می‌شود.
    """
    sub: str | None = None # subject یا همان شناسه کاربر

class LoginRequest(BaseModel):
    """
    اسکیمای ورودی برای فرم لاگین.
    کاربر باید این دو فیلد را ارسال کند.
    """
    username: str # ما از شماره موبایل به عنوان نام کاربری استفاده می‌کنیم
    password: str
