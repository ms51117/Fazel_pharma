# Import all models here for easy access and to ensure they're registered
from .user import User
from .user_role import UserRole
from .patient import Patient
from .disease_type import DiseaseType
from .drug import Drug
from .order import Order
from .order_list import OrderList
from .payment_list import PaymentList
from .message import Message
from .drug_map import DrugMap
from .user_role_permission import UserRolePermission
from .bot_message import BotMessage

# This allows: from app.models import User, Role, etc.
__all__ = [
    "User",
    "UserRole",
    "UserRolePermission",
    "Patient",
    "DiseaseType",
    "OrderList",
    "Drug",
    "Order",
    "PaymentList",
    "Message",
    "DrugMap",
    "BotMessage"

]


