# app/schemas/user.py

from typing import Optional
from sqlmodel import SQLModel,Field
from datetime import datetime
from app.models.user import UserBase  # Import UserBase from your model file


# Schema for creating a new user.
# It inherits fields from UserBase and adds a 'password' field.
class UserCreate(UserBase):
    """
    Schema for creating a user. This is what the API expects as input.
    """
    # Plain password, which will be hashed before saving.
    password: str

    # role_id is optional during creation, can be set later.
    role_id: Optional[int] = None

    mobile_number : Optional[str] = None



# Schema for reading user data.
# This is what the API will return as output.
class UserRead(UserBase):
    """
    Schema for reading user information. Excludes sensitive data.
    """
    # Include fields from the User model that are not in UserBase.
    user_id: int
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    role_id: Optional[int] = None
    mobile_number : Optional[str] = None


# Schema for updating an existing user.
# All fields are optional, so the client can update only what's needed.
class UserUpdate(SQLModel):
    """
    Schema for updating a user. All fields are optional.
    """
    full_name: Optional[str]|None = None
    national_code: Optional[str]|None = None
    mobile_number: Optional[str] |None = None
    address: Optional[str] |None = None
    is_active: Optional[bool] |None = None
    is_verified: Optional[bool] |None = None
    role_id: Optional[int] |None = None


class UserRoleRead(SQLModel):
    """
    Schema for reading a user's role.
    Used by the bot to determine user workflow.
    """
    role_name: str | None = Field(default=None, alias="roleName")

    class Config:
        populate_by_name = True # Allows using alias "roleName"