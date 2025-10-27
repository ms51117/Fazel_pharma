# app/routes/order.py

from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import sql



from app.core.permission import FormName, PermissionAction, RoleChecker
from database import get_session
from app.models.order import Order
from app.models.patient import Patient
from app.models.user import User
from app.schemas.order import OrderCreate, OrderRead, OrderUpdate , OrderReadWithDetails
from security import get_current_active_user
from app.models.drug import Drug
from app.models.order_list import OrderList

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
    db_order = Order.model_validate({
        "patient_id": order_in.patient_id,
        "user_id": order_in.user_id,
        # status به طور پیش‌فرض "created" خواهد بود
    })
    session.add(db_order)
    await session.commit()
    await session.refresh(db_order)

    statement = select(Drug).where(Drug.drugs_id.in_(order_in.drug_ids))
    result = await session.execute(statement)
    drugs_to_add = result.scalars().all()

    # Map drug_id to its price for easy lookup
    drug_price_map = {drug.drugs_id: drug.price for drug in drugs_to_add}

    items_to_add = []
    for drug_id in order_in.drug_ids:
        price = drug_price_map.get(drug_id)
        if price is None:
            # اگر به هر دلیلی دارویی یافت نشد، از آن صرف نظر کن
            # می‌توانید اینجا لاگ هم ثبت کنید
            continue

        order_list_item = OrderList(
            order_id=db_order.order_id,
            drug_id=drug_id,
            qty=1,  # فعلا تعداد را ۱ در نظر می‌گیریم
            price=price
        )
        items_to_add.append(order_list_item)

    if items_to_add:
        session.add_all(items_to_add)  # استفاده از add_all برای کارایی بیشتر
        await session.commit()

    # Refresh the order object to load the newly created order_list items
    await session.refresh(db_order, attribute_names=["order_list"])

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
