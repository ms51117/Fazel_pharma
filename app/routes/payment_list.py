# app/routes/payment_list.py

from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import selectinload
from sqlmodel import select,Date
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from app.models.payment_list import PaymentList
from app.models.user import User
from app.models.order import Order
from app.schemas.payment_list import PaymentListCreate, PaymentListRead, PaymentListUpdate, DatePaymentListRead
from security import get_current_active_user

#  for role check - this is the name define in database
from app.core.permission import FormName, PermissionAction, RoleChecker
from app.core.enums import PaymentStatusEnum
from datetime import date




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

# -----------------------------------------------------------------------------------------------



# اندپوینت ۱: دریافت تاریخ‌هایی که پرداخت در انتظار دارند
@router.get("/not-seen/", response_model=list[str])
async def get_pending_payment_dates(
        *,
        current_user: User = Depends(get_current_active_user),
        _permission_check: None = Depends(
            RoleChecker(form_name=FormName.PAYMENT_LIST, required_permission=PermissionAction.DELETE)),

        session: AsyncSession = Depends(get_session),
):
    """
    Returns a list of unique dates (YYYY-MM-DD) that have payments
    with 'Pending' status.
    """
    statement = select(func.date(Order.created_at)).join(PaymentList).where(PaymentList.payment_status == PaymentStatusEnum.NOT_SEEN).distinct()
    result = await session.exec(statement)
    results= result.all()
    # تبدیل تاریخ‌ها به رشته
    return [str(date) for date in results]

# اندپوینت ۲: دریافت لیست بیماران/پرداخت‌های منتظر در یک تاریخ خاص
@router.get("/not-seen/by-date/{date_str}", response_model=list[DatePaymentListRead]) # ممکن است نیاز به اسکیمای بهتری داشته باشد
async def get_pending_payments_by_date(
        *,
        current_user: User = Depends(get_current_active_user),
        _permission_check: None = Depends(
            RoleChecker(form_name=FormName.PAYMENT_LIST, required_permission=PermissionAction.DELETE)),

        date_str: date,
        session: AsyncSession = Depends(get_session),
):
    """
    Returns a list of pending payments for a specific date, including patient info.
    """
    statement = (
        select(PaymentList)
        .join(Order)
        .options(selectinload(PaymentList.order).selectinload(Order.patient)) # برای دسترسی به بیمار
        .where(PaymentList.payment_status == PaymentStatusEnum.NOT_SEEN)
        .where(func.cast(Order.created_at,Date) == date_str)
    )
    result = await session.exec(statement)
    payments = result.all()

    # --- بخش اصلاح شده: ساخت دستی خروجی ---
    output_list = []
    for pay in payments:
        # 1. استخراج آبجکت بیمار از داخل اردر
        # بررسی می‌کنیم که اردر و بیمار وجود داشته باشند تا ارور ندهد
        patient = pay.order.patient if (pay.order and pay.order.patient) else None

        # 2. ساخت نام کامل
        if patient:
            full_name_str = patient.full_name or ""
            tg_id = str(patient.telegram_id) if patient.telegram_id else None
        else:
            full_name_str = "ناشناس"
            tg_id = None

        if not full_name_str:  # اگر نام و فامیل خالی بود
            full_name_str = f"کاربر {tg_id}" if tg_id else "ناشناس"

        # 3. تبدیل آبجکت دیتابیس به دیکشنری و اضافه کردن فیلدهای دستی
        # model_dump() اطلاعات خودِ جدول PaymentList را دیکشنری می‌کند
        pay_dict = pay.model_dump()

        # فیلدهای اضافه مدل DatePaymentListRead را پر می‌کنیم
        pay_dict["full_name"] = full_name_str
        pay_dict["telegram_id"] = tg_id

        # اضافه کردن به لیست خروجی
        output_list.append(pay_dict)

    return output_list


@router.get("/by-order/{order_id}", response_model=List[PaymentListRead])
async def read_payments_by_order_id(
        *,
        current_user: User = Depends(get_current_active_user),
        order_id: int,
        _permission_check: None = Depends(
            RoleChecker(form_name=FormName.PAYMENT_LIST, required_permission=PermissionAction.VIEW)),
        session: AsyncSession = Depends(get_session),
) -> Any:
    """
    دریافت تمام پرداختی‌های مرتبط با یک سفارش خاص.
    خروجی لیستی از پرداخت‌هاست (ممکن است خالی باشد).
    """
    statement = select(PaymentList).where(PaymentList.order_id == order_id)
    result = await session.exec(statement)
    payments = result.all()  # <--- تغییر مهم: دریافت لیست نتایج از Result

    # اگر می‌خواهید در صورت نبودن هیچ پرداختی، لیست خالی برگردد (توصیه می‌شود):
    return payments

    # اگر حتماً می‌خواهید ارور 404 بدهد (وقتی هیچ پرداختی نیست):
    # if not payments:
    #     raise HTTPException(
    #         status_code=status.HTTP_404_NOT_FOUND,
    #         detail=f"No payments found for order ID {order_id}",
    #     )
    # return payments