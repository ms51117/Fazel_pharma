# /security.py

from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from sqlmodel import select
from sqlalchemy.orm import selectinload
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import UserRole
from setting import settings
from database import get_session
from app.models.user import User
from app.schemas.token import TokenPayload

from app.core.permission import FormName, PermissionAction


# Context برای هش کردن و بررسی رمز عبور
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# این اسکما فقط برای این است که به Swagger بگوییم اندپوینت لاگین کجاست
# و باعث می‌شود در اندپوینت /login فرم username/password نمایش داده شود.
# ما از این اسکما برای محافظت از روت‌های دیگر استفاده *نخواهیم* کرد.
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"/login/access-token"
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
        # همان وابستگی شما که به درستی کار می‌کند
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> User:
    """
    وابستگی (Dependency) برای دریافت کاربر فعلی از توکن JWT.
    این نسخه بهینه شده و اطلاعات نقش (Role) و دسترسی‌های (Permissions) کاربر را نیز
    همزمان با خود کاربر بارگذاری می‌کند.
    """
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise credentials_exception

    mobile_number = token_data.sub

    # === فقط این بخش تغییر می‌کند (بهینه‌سازی کوئری) ===
    # به جای select ساده، از selectinload برای بارگذاری روابط مرتبط استفاده می‌کنیم.
    statement = (
        select(User)
        .where(User.mobile_number == mobile_number)
        .options(
            # به SQLAlchemy/SQLModel می‌گوید:
            # "وقتی کاربر را پیدا کردی، بلافاصله role آن را هم با یک JOIN بگیر"
            # "و سپس user_role_permission های مربوط به آن role را هم با یک JOIN دیگر بگیر"
            selectinload(User.role).selectinload(UserRole.user_role_permission)
        )
    )
    # از exec برای اجرای کوئری statement استفاده می‌کنیم
    result = await session.exec(statement)
    user = result.one_or_none()
    # =================================================

    if user is None:
        raise credentials_exception

    return user


# ========= تابع جدید برای اضافه کردن =========

async def get_current_active_user(
        # این تابع از تابع get_current_user شما استفاده می‌کند
        current_user: User = Depends(get_current_user),
) -> User:
    """
    وابستگی اصلی برای اندپوینت‌های محافظت شده.
    کاربر را از get_current_user می‌گیرد و چک می‌کند که آیا فعال (is_active) است یا خیر.
    """
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    return current_user


# ========= پایان تغییرات =========

# کلاس RoleChecker که در پیام قبلی معرفی شد را هم اینجا اضافه کنید
class RoleChecker:
    """
    Dependency class to check user permissions based on their role.
    """

    def __init__(self, form_name: FormName, required_permission: PermissionAction):
        self.form_name = form_name.value

        self.required_permission = required_permission.value

    def __call__(self, current_user: User = Depends(get_current_active_user)):
        """
        This method is executed when the dependency is called by FastAPI.
        """
        if not current_user.role or not current_user.role.user_role_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You do not have permission to perform '{self.required_permission}' on '{self.form_name}'.",
            )

        permission_found = False
        for perm in current_user.role.user_role_permission:
            if perm.form_name == self.form_name:
                permission_found = True
                if not getattr(perm, self.required_permission, False):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"You do not have permission to perform '{self.required_permission}' on '{self.form_name}'.",
                    )
                break

        if not permission_found:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No permissions defined for form '{self.form_name}' in your role.",
            )