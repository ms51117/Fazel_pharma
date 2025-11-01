# app/routes/payment_list.py

from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from app.models.payment_list import PaymentList
from app.models.user import User
from app.models.order import Order
from app.schemas.payment_list import PaymentListCreate, PaymentListRead, PaymentListUpdate
from security import get_current_active_user

#  for role check - this is the name define in database
from app.core.permission import FormName, PermissionAction, RoleChecker


router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=PaymentListRead)
async def create_payment(
        *,
        current_user: User = Depends(get_current_active_user),
        _permission_check: None = Depends(
            RoleChecker(form_name=FormName.PAYMENT_LIST, required_permission=PermissionAction.INSERT)),

        session: AsyncSession = Depends(get_session),
        payment_in: PaymentListCreate,
) -> Any:
    """
    ثبت یک پرداخت جدید.
    """
    # 1. بررسی وجود کاربر (User)
    order = await session.get(Order, payment_in.order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID {payment_in.order_id} not found. Cannot create payment."
        )

    # 2. ایجاد آبجکت و ذخیره در دیتابیس
    db_payment = PaymentList.model_validate(payment_in)
    session.add(db_payment)
    await session.commit()
    await session.refresh(db_payment)
    return db_payment


@router.get("/", response_model=List[PaymentListRead])
async def read_payments(
        *,
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_session),
        _permission_check: None = Depends(
            RoleChecker(form_name=FormName.PAYMENT_LIST, required_permission=PermissionAction.VIEW)),

        skip: int = 0,
        limit: int = 100,
) -> Any:
    """
    دریافت لیست تمام پرداخت‌ها.
    """
    statement = select(PaymentList).offset(skip).limit(limit)
    payments = (await session.exec(statement)).all()
    return payments


@router.get("/{payment_id}", response_model=PaymentListRead)
async def read_payment_by_id(
        *,
        current_user: User = Depends(get_current_active_user),
        payment_id: int,
        _permission_check: None = Depends(
            RoleChecker(form_name=FormName.PAYMENT_LIST, required_permission=PermissionAction.VIEW)),

        session: AsyncSession = Depends(get_session),
) -> Any:
    """
    دریافت اطلاعات یک پرداخت با شناسه (ID).
    """
    payment = await session.get(PaymentList, payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payment with ID {payment_id} not found",
        )
    return payment


@router.patch("/{payment_id}", response_model=PaymentListRead)
async def update_payment(
        *,
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_session),
        _permission_check: None = Depends(
            RoleChecker(form_name=FormName.PAYMENT_LIST, required_permission=PermissionAction.UPDATE)),

        payment_id: int,
        payment_in: PaymentListUpdate,
) -> Any:
    """
    آپدیت اطلاعات یک پرداخت موجود.
    """
    db_payment = await session.get(PaymentList, payment_id)
    if not db_payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payment with ID {payment_id} not found",
        )

    update_data = payment_in.model_dump(exclude_unset=True)

    # اگر user_id در حال تغییر است، وجود کاربر جدید را بررسی کن
    if "user_id" in update_data:
        user = await session.get(User, update_data["user_id"])
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {update_data['user_id']} not found."
            )

    db_payment.sqlmodel_update(update_data)
    session.add(db_payment)
    await session.commit()
    await session.refresh(db_payment)
    return db_payment


@router.delete("/{payment_id}")
async def delete_payment(
        *,
        current_user: User = Depends(get_current_active_user),
        _permission_check: None = Depends(
            RoleChecker(form_name=FormName.PAYMENT_LIST, required_permission=PermissionAction.DELETE)),

        payment_id: int,
        session: AsyncSession = Depends(get_session),
):
    """
    حذف یک پرداخت با شناسه (ID).
    """
    payment = await session.get(PaymentList, payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payment with ID {payment_id} not found",
        )

    await session.delete(payment)
    await session.commit()
    return {"ok": True, "message": "Payment deleted successfully"}
