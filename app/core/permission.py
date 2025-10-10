# app/core/permissions.py
from enum import Enum

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
