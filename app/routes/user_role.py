# app/routes/user_role.py

from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from app.models.user_role import UserRole
from app.schemas.user_role import UserRoleCreate, UserRoleRead, UserRoleUpdate
from app.models.user import User
from security import get_current_active_user


#  for role check - this is the name define in database
from app.core.permission import FormName, PermissionAction, RoleChecker


router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserRoleRead)
async def create_role(
        *,
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_session),
        role_in: UserRoleCreate,
        _permission_check: None = Depends(
            RoleChecker(form_name=FormName.USER_ROLES, required_permission=PermissionAction.INSERT)),

) -> Any:
    """
    ایجاد یک نقش کاربری جدید (مثلا: ادمین، مشاور).
    """
    # بررسی تکراری بودن نام نقش
    statement = select(UserRole).where(UserRole.role_name == role_in.role_name)
    existing_role = (await session.exec(statement)).first()
    if existing_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Role with name '{role_in.role_name}' already exists."
        )

    db_role = UserRole.model_validate(role_in)
    session.add(db_role)
    await session.commit()
    await session.refresh(db_role)
    return db_role


@router.get("/", response_model=List[UserRoleRead])
async def read_roles(
        *,
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_session),
        _permission_check: None = Depends(
            RoleChecker(form_name=FormName.USER_ROLES, required_permission=PermissionAction.VIEW)),

        skip: int = 0,
        limit: int = 100,
) -> Any:
    """
    دریافت لیست تمام نقش‌ها.
    """
    statement = select(UserRole).offset(skip).limit(limit)
    roles = (await session.exec(statement)).all()
    return roles


@router.get("/{role_id}", response_model=UserRoleRead)
async def read_role_by_id(
        *,
        current_user: User = Depends(get_current_active_user),
        role_id: int,
        session: AsyncSession = Depends(get_session),
        _permission_check: None = Depends(
            RoleChecker(form_name=FormName.USER_ROLES, required_permission=PermissionAction.VIEW))

) -> Any:
    """
    دریافت اطلاعات یک نقش با شناسه (ID).
    """
    role = await session.get(UserRole, role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role with ID {role_id} not found",
        )
    return role


@router.patch("/{role_id}", response_model=UserRoleRead)
async def update_role(
        *,
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_session),
        _permission_check: None = Depends(
            RoleChecker(form_name=FormName.USER_ROLES, required_permission=PermissionAction.UPDATE)),

        role_id: int,
        role_in: UserRoleUpdate,
) -> Any:
    """
    آپدیت اطلاعات یک نقش موجود.
    """
    db_role = await session.get(UserRole, role_id)
    if not db_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role with ID {role_id} not found",
        )

    update_data = role_in.model_dump(exclude_unset=True)
    db_role.sqlmodel_update(update_data)

    session.add(db_role)
    await session.commit()
    await session.refresh(db_role)
    return db_role


@router.delete("/{role_id}")
async def delete_role(
        *,
        current_user: User = Depends(get_current_active_user),
        _permission_check: None = Depends(
            RoleChecker(form_name=FormName.USER_ROLES, required_permission=PermissionAction.DELETE)),

        role_id: int,
        session: AsyncSession = Depends(get_session),
):
    """
    حذف یک نقش با شناسه (ID).
    """
    role = await session.get(UserRole, role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role with ID {role_id} not found",
        )

    await session.delete(role)
    await session.commit()
    return {"ok": True, "message": "Role deleted successfully"}
