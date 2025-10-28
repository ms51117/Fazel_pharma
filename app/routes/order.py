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
    statement = (select(Order)
                 .where(Order.order_id == order_id)
                 .options(selectinload(Order.order_list),selectinload(Order.payment_list)))
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
        order_in: OrderComprehensiveUpdate,  # استفاده از اسکیمای جامع جدید
) -> Any:
    """
    A comprehensive endpoint to update an order.
    - Can update 'order_status'.
    - Can replace the entire list of 'order_items'.
    All operations are optional and transactional.
    """
    # 1. سفارش را به همراه آیتم‌های فعلی‌اش (order_lists) با Eager Loading دریافت کن
    statement = (
        select(Order)
        .where(Order.order_id == order_id)
        .options(selectinload(Order.order_lists))  # بسیار مهم برای دسترسی و حذف آیتم‌ها
    )
    result = await session.exec(statement)
    db_order = result.one_or_none()

    if not db_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID {order_id} not found",
        )

    # یک فلگ برای اینکه بفهمیم آیا تغییری اعمال شده است یا خیر
    is_updated = False
    update_data = order_in.model_dump(exclude_unset=True)

    # 2. آپدیت وضعیت سفارش (اگر در درخواست آمده باشد)
    if "order_status" in update_data:
        db_order.order_status = order_in.order_status
        is_updated = True

    # 3. جایگزینی لیست داروها (اگر در درخواست آمده باشد)
    if "order_items" in update_data:
        # --- الف) حذف تمام آیتم‌های قدیمی ---
        for item in db_order.order_lists:
            await session.delete(item)

        # --- ب) اعتبارسنجی و آماده‌سازی آیتم‌های جدید ---
        new_items_data = order_in.order_items
        if new_items_data:  # اگر لیست خالی نباشد
            drug_ids = {item.drug_id for item in new_items_data}

            # با یک کوئری تمام داروهای مورد نیاز را بگیر
            drug_stmt = select(Drug).where(Drug.drugs_id.in_(drug_ids))
            drugs_result = await session.exec(drug_stmt)
            valid_drugs = drugs_result.all()

            # بررسی اینکه تمام ID های درخواستی معتبر هستند
            if len(valid_drugs) != len(drug_ids):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="One or more drug IDs are invalid."
                )

            # یک دیکشنری از قیمت‌ها برای دسترسی سریع و امن
            drug_price_map = {drug.drugs_id: drug.price for drug in valid_drugs}

            # --- ج) ایجاد و افزودن آیتم‌های جدید به session ---
            for item_data in new_items_data:
                new_order_item = OrderList(
                    order_id=db_order.order_id,
                    drug_id=item_data.drug_id,
                    qty=item_data.qty,
                    price=drug_price_map[item_data.drug_id]  # قیمت از دیتابیس خوانده می‌شود
                )
                session.add(new_order_item)

        is_updated = True

    # 4. ذخیره‌سازی تغییرات در دیتابیس (فقط اگر تغییری وجود داشته باشد)
    if is_updated:
        db_order.updated_at = datetime.now(timezone.utc)
        session.add(db_order)
        await session.commit()

        # Refresh کردن آبجکت سفارش برای بارگذاری مجدد روابط (به خصوص order_lists جدید)
        await session.refresh(db_order, attribute_names=["order_lists"])

    # برای اطمینان از اینکه همه روابط برای پاسخ JSON آماده هستند، دوباره آن‌ها را load میکنیم
    # این کار از خطای MissingGreenlet در پاسخ نهایی جلوگیری می‌کند
    final_order_statement = (
        select(Order)
        .where(Order.order_id == order_id)
        .options(selectinload(Order.order_lists), selectinload(Order.payment_list))
    )
    final_result = await session.exec(final_order_statement)

    return final_result.one()


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
@router.get("/get-order-by-status-by-patient-id/{patient_id}/{status}", response_model=list[OrderReadWithDetails])
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
                 .options(selectinload(Order.order_list),selectinload(Order.payment_list)))
    result = await session.exec(statement)
    orders = result.all()


    return orders

