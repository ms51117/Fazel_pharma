# app/routes/order.py

from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.permission import FormName, PermissionAction
from database import get_session
from app.models.order import Order
from app.models.patient import Patient
from app.models.user import User
from app.schemas.order import OrderCreate, OrderRead, OrderUpdate , OrderReadWithDetails
from security import get_current_active_user, RoleChecker

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=OrderRead)
async def create_order(
        *,
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_session),
        _permission_check: None = Depends(
            RoleChecker(form_name=FormName.ORDER, required_permission=PermissionAction.INSERT)),
        order_in: OrderCreate,
) -> Any:
    """
    ایجاد یک سفارش جدید برای یک بیمار توسط یک کاربر.
    """
    # 1. بررسی وجود بیمار (Patient)
    patient = await session.get(Patient, order_in.patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {order_in.patient_id} not found."
        )

    # 2. بررسی وجود کاربر (User)
    user = await session.get(User, order_in.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {order_in.user_id} not found."
        )

    # 3. ایجاد آبجکت و ذخیره در دیتابیس
    db_order = Order.model_validate(order_in)
    session.add(db_order)
    await session.commit()
    await session.refresh(db_order)
    return db_order


@router.get("/", response_model=List[OrderRead])
async def read_orders(
        *,
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_session),
        _permission_check: None = Depends(
            RoleChecker(form_name=FormName.ORDER, required_permission=PermissionAction.VIEW)),
        skip: int = 0,
        limit: int = 100,
) -> Any:
    """
    دریافت لیست تمام سفارش‌ها.
    """
    statement = select(Order).offset(skip).limit(limit)
    orders = (await session.exec(statement)).all()
    return orders


@router.get("/{order_id}", response_model=OrderReadWithDetails)
async def read_order_by_id(
        *,
        current_user: User = Depends(get_current_active_user),
        _permission_check: None = Depends(
            RoleChecker(form_name=FormName.ORDER, required_permission=PermissionAction.VIEW)),
        order_id: int,
        session: AsyncSession = Depends(get_session),
) -> Any:
    """
    دریافت اطلاعات یک سفارش با شناسه (ID) به همراه تمام اقلام آن.
    """
    # از selectinload برای Eager Loading اقلام سفارش استفاده می‌کنیم.
    statement = select(Order).where(Order.order_id == order_id).options(selectinload(Order.order_list))
    result = await session.exec(statement)
    order = result.one_or_none()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID {order_id} not found",
        )
    return order

@router.patch("/{order_id}", response_model=OrderRead)
async def update_order(
        *,
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_session),
        _permission_check: None = Depends(
            RoleChecker(form_name=FormName.ORDER, required_permission=PermissionAction.UPDATE)),
        order_id: int,
        order_in: OrderUpdate,
) -> Any:
    """
    آپدیت اطلاعات یک سفارش موجود.
    """
    db_order = await session.get(Order, order_id)
    if not db_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID {order_id} not found",
        )

    update_data = order_in.model_dump(exclude_unset=True)

    # اعتبارسنجی کلیدهای خارجی در صورت تغییر
    if "patient_id" in update_data:
        patient = await session.get(Patient, update_data["patient_id"])
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

    if "user_id" in update_data:
        user = await session.get(User, update_data["user_id"])
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

    db_order.sqlmodel_update(update_data)
    session.add(db_order)
    await session.commit()
    await session.refresh(db_order)
    return db_order


@router.delete("/{order_id}")
async def delete_order(
        *,
        current_user: User = Depends(get_current_active_user),
        order_id: int,
        session: AsyncSession = Depends(get_session),
        _permission_check: None = Depends(
            RoleChecker(form_name=FormName.ORDER, required_permission=PermissionAction.DELETE)),
):
    """
    حذف یک سفارش با شناسه (ID).
    توجه: این کار باعث حذف تمام اقلام و پرداخت‌های مرتبط نیز خواهد شد (Cascade).
    """
    order = await session.get(Order, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID {order_id} not found",
        )

    await session.delete(order)
    await session.commit()
    return {"ok": True, "message": "Order and its related items deleted successfully"}
