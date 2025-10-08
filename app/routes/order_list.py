# app/routes/order_list.py

from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from app.models.order_list import OrderList
from app.models.order import Order
from app.models.drug import Drug # بعد از پیاده‌سازی Drug اضافه می‌شود
from app.schemas.order_list import OrderListCreate, OrderListRead, OrderListUpdate
from security import get_current_active_user
from app.models.user import User

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=OrderListRead)
async def create_order_item(
        *,
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_session),
        order_item_in: OrderListCreate,
) -> Any:
    """
    افزودن یک قلم جدید به یک سفارش موجود.
    """
    # 1. بررسی وجود سفارش (Order)
    order = await session.get(Order, order_item_in.order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID {order_item_in.order_id} not found."
        )

    # 2. بررسی وجود دارو (Drug) - تکمیل TODO
    drug = await session.get(Drug, order_item_in.drug_id)  # <--- این خط را اضافه کنید
    if not drug:  # <--- این بلاک را اضافه کنید
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Drug with ID {order_item_in.drug_id} not found."
        )

    # 3. ایجاد آبجکت و ذخیره در دیتابیس
    db_order_item = OrderList.model_validate(order_item_in)
    session.add(db_order_item)
    await session.commit()
    await session.refresh(db_order_item)
    return db_order_item

@router.get("/", response_model=List[OrderListRead])
async def read_order_items(
        *,
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_session),
        skip: int = 0,
        limit: int = 100,
) -> Any:
    """
    دریافت لیست تمام اقلام سفارش‌ها.
    """
    statement = select(OrderList).offset(skip).limit(limit)
    order_items = (await session.exec(statement)).all()
    return order_items


@router.get("/{order_list_id}", response_model=OrderListRead)
async def read_order_item_by_id(
        *,
        current_user: User = Depends(get_current_active_user),
        order_list_id: int,
        session: AsyncSession = Depends(get_session),
) -> Any:
    """
    دریافت اطلاعات یک قلم سفارش با شناسه (ID).
    """
    order_item = await session.get(OrderList, order_list_id)
    if not order_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order item with ID {order_list_id} not found",
        )
    return order_item


@router.patch("/{order_list_id}", response_model=OrderListRead)
async def update_order_item(
        *,
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_session),
        order_list_id: int,
        order_item_in: OrderListUpdate,
) -> Any:
    """
    آپدیت اطلاعات یک قلم سفارش موجود (مثلاً تعداد).
    """
    db_order_item = await session.get(OrderList, order_list_id)
    if not db_order_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order item with ID {order_list_id} not found",
        )

    update_data = order_item_in.model_dump(exclude_unset=True)
    db_order_item.sqlmodel_update(update_data)
    session.add(db_order_item)
    await session.commit()
    await session.refresh(db_order_item)
    return db_order_item


@router.delete("/{order_list_id}")
async def delete_order_item(
        *,
        current_user: User = Depends(get_current_active_user),
        order_list_id: int,
        session: AsyncSession = Depends(get_session),
):
    """
    حذف یک قلم سفارش با شناسه (ID).
    """
    order_item = await session.get(OrderList, order_list_id)
    if not order_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order item with ID {order_list_id} not found",
        )

    await session.delete(order_item)
    await session.commit()
    return {"ok": True, "message": "Order item deleted successfully"}
