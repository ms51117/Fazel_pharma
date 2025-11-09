# admin_auth.py

from typing import Optional
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.responses import RedirectResponse
from sqlmodel import select  # ایمپورت کردن select از sqlmodel

# ایمپورت کردن session_maker که در مرحله قبل ساختیم
from database import async_session_maker
from app.models.user import User
from security import verify_password

import os
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        mobile_number, password = form["username"], form["password"]

        # تغییر کلیدی: استفاده از async with و کوئری جدید
        async with async_session_maker() as session:
            statement = select(User).where(User.mobile_number == mobile_number)
            result = await session.exec(statement)
            user = result.first()

        if not user:
            return False

        # فرض می‌کنیم شما یک فیلد is_superuser در مدل User دارید
        # اگر ندارید، این شرط را بردارید یا با منطق خودتان جایگزین کنید
        # if not user.is_superuser:
        #     return False

        if not verify_password(password, user.hashed_password):
            return False

        request.session.update({"mobile_number": user.mobile_number})
        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> Optional[RedirectResponse]:
        mobile_number = request.session.get("mobile_number")

        if not mobile_number:
            return RedirectResponse(request.url_for("admin:login"), status_code=302)

        # تغییر کلیدی: استفاده از async with و کوئری جدید
        async with async_session_maker() as session:
            statement = select(User).where(User.mobile_number == mobile_number)
            result = await session.exec(statement)
            user = result.first()

        # اگر کاربر در دیتابیس پیدا نشد یا دیگر ادمین نبود
        if not user:  # or not user.is_superuser:
            return RedirectResponse(request.url_for("admin:login"), status_code=302)

        request.state.user = user
        return True


# اطمینان حاصل کنید که متغیر SECRET_KEY را پاس می‌دهید، نه رشته "SECRET_KEY"
authentication_backend = AdminAuth(secret_key=SECRET_KEY)
