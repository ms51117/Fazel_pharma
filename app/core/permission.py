# app/core/permissions.py
from enum import Enum

from fastapi import Depends, HTTPException, status # <<-- اضافه شده
from app.models.user import User                   # <<-- اضافه شده
from security import get_current_active_user   # <<-- اضافه شده


class PermissionAction(str, Enum):
    """
    Defines the types of actions a user can perform.
    Using (str, Enum) makes it compatible with FastAPI/Pydantic.
    """
    VIEW = "view"
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"

class FormName(str, Enum):
    """
    Defines the names of all forms/modules in the application.
    This is the single source of truth for form names.
    """
    # --- User Management ---
    USER = "User"
    USER_ROLES = "UserRoles"
    USER_ROLE_PERMISSIONS = "UserRolePermissions"

    # --- Patient Management ---
    PATIENT = "Patient"

    # --- Orders ---
    ORDER_LIST = "OrderList"
    ORDER = "Order"

    # --- Payments ---
    PAYMENT_LIST = "PaymentList"

    # --- Message ---
    MESSAGE = "Message"

    # --- Drug and Disease ---
    DRUG = "Drug"
    DISEASE_TYPE = "DiseaseType"
    DRUG_MAP = "DrugMap"

    # ... سایر فرم‌ها را به همین ترتیب اضافه کنید




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