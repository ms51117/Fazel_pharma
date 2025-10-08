# app/routes/user_role_permission.py

from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from app.models.user_role_permission import UserRolePermission
from app.schemas.user_role_permission import UserRolePermissionCreate, UserRolePermissionRead, UserRolePermissionUpdate
from app.models.user import User
from security import get_current_active_user


router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserRolePermissionRead)
async def create_permission(
        *,
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_session),
        permission_in: UserRolePermissionCreate,
) -> Any:
    """
    ایجاد یک سطح دسترسی جدید.
    """
    # بررسی تکراری بودن دسترسی برای یک فرم و نقش خاص
    statement = select(UserRolePermission).where(
        UserRolePermission.form_name == permission_in.form_name,
        UserRolePermission.role_id == permission_in.role_id
    )
    existing_permission = (await session.exec(statement)).first()
    if existing_permission:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Permission for this form_name and role_id already exists."
        )

    db_permission = UserRolePermission.model_validate(permission_in)
    session.add(db_permission)
    await session.commit()
    await session.refresh(db_permission)
    return db_permission


@router.get("/", response_model=List[UserRolePermissionRead])
async def read_permissions(
        *,
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_session),
        skip: int = 0,
        limit: int = 100,
) -> Any:
    """
    دریافت لیست تمام سطوح دسترسی.
    """
    statement = select(UserRolePermission).offset(skip).limit(limit)
    permissions = (await session.exec(statement)).all()
    return permissions


@router.get("/{permission_id}", response_model=UserRolePermissionRead)
async def read_permission_by_id(
        *,
        current_user: User = Depends(get_current_active_user),
        permission_id: int,
        session: AsyncSession = Depends(get_session),
) -> Any:
    """
    دریافت اطلاعات یک دسترسی خاص با شناسه (ID).
    """
    permission = await session.get(UserRolePermission, permission_id)
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Permission with ID {permission_id} not found",
        )
    return permission


@router.patch("/{permission_id}", response_model=UserRolePermissionRead)
async def update_permission(
        *,
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_session),
        permission_id: int,
        permission_in: UserRolePermissionUpdate,
) -> Any:
    """
    آپدیت اطلاعات یک دسترسی موجود.
    """
    db_permission = await session.get(UserRolePermission, permission_id)
    if not db_permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Permission with ID {permission_id} not found",
        )

    update_data = permission_in.model_dump(exclude_unset=True)
    db_permission.sqlmodel_update(update_data)

    session.add(db_permission)
    await session.commit()
    await session.refresh(db_permission)
    return db_permission


@router.delete("/{permission_id}")
async def delete_permission(
        *,
        current_user: User = Depends(get_current_active_user),
        permission_id: int,
        session: AsyncSession = Depends(get_session),
):
    """
    حذف یک دسترسی با شناسه (ID).
    """
    permission = await session.get(UserRolePermission, permission_id)
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Permission with ID {permission_id} not found",
        )

    await session.delete(permission)
    await session.commit()
    # طبق الگوی patient.py، برای حذف موفقیت آمیز، پاسخ ۲۰۰ با یک پیام مناسب برمیگردانیم
    return {"ok": True, "message": "Permission deleted successfully"}
