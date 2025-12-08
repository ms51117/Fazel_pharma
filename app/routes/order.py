# app/routes/order.py

from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import sql
from datetime import datetime, timezone

from app.core.enums import OrderStatusEnum
from app.core.permission import FormName, PermissionAction, RoleChecker
from database import get_session
from app.models.order import Order
from app.models.patient import Patient
from app.models.user import User
from app.schemas.order import OrderCreate, OrderRead, OrderUpdate, OrderReadWithDetails, OrderComprehensiveUpdate
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

    target_drug_ids = [item.drug_id for item in order_in.items]

    statement = select(Drug).where(Drug.drugs_id.in_(target_drug_ids))
    result = await session.execute(statement)
    found_drugs = result.scalars().all()

    # ب) ساخت مپ قیمت (ID -> Price)
    drug_price_map = {drug.drugs_id: drug.price for drug in found_drugs}

    items_to_add = []

    # ج) حلقه روی آیتم‌های ورودی (که شامل qty هستند)
    for item in order_in.items:
        price = drug_price_map.get(item.drug_id)

        if price is None:
            # اگر دارو پیدا نشد (مثلاً آیدی اشتباه بود)، لاگ کنید و رد شوید
            continue

        order_list_item = OrderList(
            order_id=db_order.order_id,
            drug_id=item.drug_id,
            qty=item.qty,  # <--- استفاده از مقدار qty ارسالی
            price=price
        )
        items_to_add.append(order_list_item)

    if items_to_add:
        session.add_all(items_to_add)
        await session.commit()

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
    statement = (
        select(Order)
        .where(Order.order_id == order_id)
        .options(selectinload(Order.order_list).selectinload(OrderList.drug),selectinload(Order.payment_list)))

    result = await session.exec(statement)
    order = result.one_or_none()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID {order_id} not found",
        )
    return order


@router.patch("/{order_id}", response_model=OrderReadWithDetails)
async def comprehensive_update_order(
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
    _permission_check: None = Depends(
        RoleChecker(form_name=FormName.ORDER, required_permission=PermissionAction.UPDATE)),
    order_id: int,
    order_in: OrderComprehensiveUpdate,
) -> Any:
    """
    A comprehensive endpoint to update an order using modern cascading.
    - Can update 'order_status'.
    - Replaces the entire list of 'order_items' safely.
    """
    # 1. Get the order with its current items using selectinload
    # <<< CRITICAL CHANGE: Use selectinload to prevent session conflicts
    statement = (
        select(Order)
        .where(Order.order_id == order_id)
        .options(selectinload(Order.order_list).selectinload(OrderList.drug),selectinload(Order.payment_list))  # <--- این خط اضافه شده است

    )
    result = await session.exec(statement)
    db_order = result.one_or_none() # Use one_or_none for safety

    if not db_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID {order_id} not found",
        )

    update_data = order_in.model_dump(exclude_unset=True)
    is_updated = False

    # 2. Update order status if present
    if "order_status" in update_data:
        db_order.order_status = order_in.order_status
        is_updated = True

    # 3. Replace the list of items using the modern cascade approach
    if "order_items" in update_data:
        new_items_data = order_in.order_items
        new_order_list_objects = []

        if new_items_data:
            drug_ids = {item.drug_id for item in new_items_data}
            drug_stmt = select(Drug).where(Drug.drugs_id.in_(drug_ids))
            drugs_result = await session.exec(drug_stmt)
            valid_drugs = {drug.drugs_id: drug for drug in drugs_result.all()}

            if len(valid_drugs) != len(drug_ids):
                invalid_ids = drug_ids - set(valid_drugs.keys())
                raise HTTPException(status_code=404, detail=f"Invalid drug IDs found: {invalid_ids}")

            for item_data in new_items_data:
                new_order_list_objects.append(
                    OrderList(
                        drug_id=item_data.drug_id,
                        qty=item_data.qty,
                        price=valid_drugs[item_data.drug_id].price
                    )
                )

        # The magic line: direct replacement triggers the cascade
        db_order.order_list = new_order_list_objects
        is_updated = True

    # 4. Commit changes if anything was updated
    if is_updated:
        # No need to add db_order to session if it's already persistent
        # session.add(db_order) # This is usually not needed for an update

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



# -----------------------------------------------------------------------
@router.get("/get-order-by-status-by-patient-id/", response_model=list[OrderReadWithDetails])
async def get_orders_by_patient_and_status(
        *,
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_session),
        _permission_check: None = Depends(
            RoleChecker(form_name=FormName.ORDER, required_permission=PermissionAction.VIEW)),
        patient_id: int,
        order_status: OrderStatusEnum
) -> Any:
    """
    ایجاد یک سفارش جدید برای یک بیمار توسط یک کاربر.
    """
    # 1. بررسی وجود بیمار (Patient)
    patient = await session.get(Patient , patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {patient_id} not found."
        )

    statement = (select(Order)
                 .where(Order.patient_id == patient_id ,Order.order_status == order_status)
                 .options(selectinload(Order.order_list).selectinload(OrderList.drug),selectinload(Order.payment_list)))
    result = await session.exec(statement)
    orders = result.all()


    return orders

