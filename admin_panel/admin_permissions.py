# admin_permissions.py

from starlette.requests import Request
from app.models.user import User
from app.models.user_role_permission import UserRolePermission
from typing import Optional

def get_permission_for_table(request: Request, table_name: str) -> dict:
    user: User = request.state.user
    DEFAULT_PERMISSIONS = {"create": False, "edit": False, "delete": False, "view": False}
    permissions_list = user.role.user_role_permission
    for perm in permissions_list:
        if perm.form_name == table_name:  # <--- خط بحرانی
            return perm
    return None