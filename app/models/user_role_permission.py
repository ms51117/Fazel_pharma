# app/models/user_role_permission.py

from typing import Optional,TYPE_CHECKING
from sqlmodel import Field, SQLModel,Relationship
from app.models.base import BaseDates

if TYPE_CHECKING:
    from app.models.user_role import UserRole




class UserRolePermissionBase(SQLModel):
    """Base model for UserRolePermission shared properties"""
    role_id: int = Field(
        foreign_key="tbl_UserRole.role_id",
        nullable=False,
        description="Reference to role"
    )
    form_name: str = Field(
        max_length=100,
        nullable=False,
        description="Form or module name"
    )
    view: bool = Field(
        default=False,
        description="View permission"
    )
    insert: bool = Field(
        default=False,
        description="Insert permission"
    )
    update: bool = Field(
        default=False,
        description="Update permission"
    )
    delete: bool = Field(
        default=False,
        description="Delete permission"
    )


class UserRolePermission(UserRolePermissionBase, BaseDates, table=True):
    """Database model for UserRolePermission table"""
    __tablename__ = "tbl_UserRolePermission"

    permission_id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Auto-incremented permission ID"
    )

# relationship
user_role: "UserRole" = Relationship(back_populates="user_role_permission")