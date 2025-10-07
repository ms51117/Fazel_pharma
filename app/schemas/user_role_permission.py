# app/schemas/user_role_permission_schema.py

from typing import Optional
from sqlmodel import SQLModel
from app.models.user_role_permission import UserRolePermissionBase

# 1. اسکیمای پایه (مشترک)
# از UserRolePermissionBase که در مدل تعریف کردیم استفاده می‌کنیم.
# این اسکیما برای ایجاد (Create) و آپدیت (Update) مناسب است.
class UserRolePermissionCreate(UserRolePermissionBase):
    pass

class UserRolePermissionUpdate(SQLModel):
    form_name: Optional[str] = None
    view: Optional[bool] = None
    insert: Optional[bool] = None
    update: Optional[bool] = None
    delete: Optional[bool] = None

# 2. اسکیمای خروجی برای نمایش (Read)
# این اسکیما ID را هم شامل می‌شود که توسط دیتابیس تولید شده.
class UserRolePermissionRead(UserRolePermissionBase):
    permission_id: int
