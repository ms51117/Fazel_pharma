# app/models/user_role.py

from typing import Optional, TYPE_CHECKING, List
from sqlmodel import Field, Relationship, SQLModel
from app.models.base import BaseDates

if TYPE_CHECKING:
    from app.models.user import User


class UserRoleBase(SQLModel):
    """Base model for UserRole shared properties"""
    role_name: str = Field(
        max_length=50,
        nullable=False,
        description="Role name"
    )
    role_type: int = Field(
        nullable=False,
        description="Role type: 0=Moshaver, 1=Sandogh, 2=Admin"
    )


class UserRole(UserRoleBase, BaseDates, table=True):
    """Database model for UserRole table (tbl_userRole)"""
    __tablename__ = "tbl_UserRole"

    role_id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Auto-incremented role ID"
    )

    # Relationships
    # users: List["User"] = Relationship(back_populates="role")
