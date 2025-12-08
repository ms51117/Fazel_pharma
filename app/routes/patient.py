# In file: app/routes/patient.py

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select, or_,func,Date
from typing import List,Any
from datetime import date

# برای استفاده از AsyncSession، باید آن را از کتابخانه مربوطه import کنید
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.permission import FormName, PermissionAction, RoleChecker
# مسیر get_session باید به نسخه async اشاره کند
from database import get_session
from app.models.patient import Patient
from app.schemas.patient import PatientCreate, PatientRead, PatientUpdate, WaitingForConsultantDatesResponse, \
    AwaitingForConsultationPatientsResponse
from security import get_current_active_user
from app.models.user import User
from app.core.enums import PatientStatus

# ایجاد روتر جدید برای مدیریت بیماران
router = APIRouter()


# ===================================================================
# 1. CREATE A NEW PATIENT
# ===================================================================
@router.post("/", response_model=PatientRead, status_code=status.HTTP_201_CREATED)
async def create_patient(
        *,
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_session),
        _permission_check: None = Depends(
            RoleChecker(form_name=FormName.PATIENT, required_permission=PermissionAction.INSERT)),
        patient_in: PatientCreate
) -> Patient:
    """
    ایجاد یک بیمار جدید در سیستم.

    - **telegram_id**: باید منحصر به فرد باشد.
    - **mobile_number**: باید منحصر به فرد باشد.
    """
    # بررسی اینکه آیا بیماری با همین mobile_number یا telegram_id قبلا ثبت شده است یا خیر
    statement = select(Patient).where(
        or_(
            # Patient.mobile_number == patient_in.mobile_number,
            Patient.telegram_id == patient_in.telegram_id
        )
    )
    existing_patient = (await session.exec(statement)).first()

    if existing_patient:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Patient with this mobile number or Telegram ID already exists."
        )

    # ایجاد نمونه از مدل دیتابیس با استفاده از داده‌های ورودی
    db_patient = Patient.model_validate(patient_in)

    session.add(db_patient)
    await session.commit()
    await session.refresh(db_patient)

    return db_patient


# ===================================================================
# 2. READ PATIENTS (List with Pagination)
# ===================================================================
@router.get("/", response_model=List[PatientRead])
async def read_patients(
        *,
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_session),
        _permission_check: None = Depends(
            RoleChecker(form_name=FormName.PATIENT, required_permission=PermissionAction.VIEW)),
        offset: int = 0,
        limit: int = Query(default=10, le=100)  # مقدار پیش‌فرض معقول‌تر و محدودیت روی 100
) -> List[Patient]:
    """
    دریافت لیست بیماران با قابلیت صفحه‌بندی (pagination).
    """
    statement = select(Patient).offset(offset).limit(limit)
    patients = (await session.exec(statement)).all()
    return patients


# ===================================================================
# 3. READ A SINGLE PATIENT BY ID
# ===================================================================
@router.get("/{telegram_id}", response_model=PatientRead)
async def read_patient(
        *,
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_session),
        _permission_check: None = Depends(
            RoleChecker(form_name=FormName.PATIENT, required_permission=PermissionAction.VIEW)),
        telegram_id: str
) -> Patient:
    """
    دریافت اطلاعات یک بیمار خاص با استفاده از شناسه (ID).
    """
    statement = select(Patient).where(Patient.telegram_id == telegram_id)

    db_patient = (await session.exec(statement)).one_or_none()

    if not db_patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    return db_patient


# ===================================================================
# 4. UPDATE A PATIENT
# ===================================================================
@router.patch("/{telegram_id}", response_model=PatientRead)
async def update_patient(
        *,
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_session),
        _permission_check: None = Depends(
            RoleChecker(form_name=FormName.PATIENT, required_permission=PermissionAction.UPDATE)),
        telegram_id: str,
        patient_in: PatientUpdate
) -> Patient:
    """
    به‌روزرسانی اطلاعات یک بیمار.
    فقط فیلدهایی که در درخواست ارسال شوند، آپدیت خواهند شد.
    """
    statement = select(Patient).where(Patient.telegram_id == telegram_id)
    db_patient = (await session.exec(statement)).one_or_none()

    if not db_patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    # استراتژی آپدیت مشابه فایل user.py
    # تبدیل داده‌های ورودی به دیکشنری و حذف مقادیر None یا ارسال نشده
    update_data = patient_in.model_dump(exclude_unset=True)

    # # به‌روزرسانی فیلدهای مدل با داده‌های جدید
    # for key, value in update_data.items():
    #     setattr(db_patient, key, value)
    db_patient.sqlmodel_update(update_data)

    session.add(db_patient)
    await session.commit()
    await session.refresh(db_patient)

    return db_patient


# ===================================================================
# 5. DELETE A PATIENT
# ===================================================================
@router.delete("/{telegram_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_patient(
        *,
        current_user: User = Depends(get_current_active_user),
        _permission_check: None = Depends(
            RoleChecker(form_name=FormName.PATIENT, required_permission=PermissionAction.DELETE)),

        session: AsyncSession = Depends(get_session),
        telegram_id: int
) -> None:
    """
    حذف یک بیمار از سیستم.
    """
    statement = select(Patient).where(Patient.telegram_id == telegram_id)
    db_patient = (await session.exec(statement)).one_or_none()

    if not db_patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    await session.delete(db_patient)
    await session.commit()

    # طبق استاندارد RESTful، پس از حذف موفق، پاسخی با status_code 204 و بدون بدنه برمیگردانیم.
    return None

# ----------------------------------------------------------------------------------

@router.get("/waiting-for-consultation-dates/", response_model=WaitingForConsultantDatesResponse)
async def waiting_for_consultation_by(
        *,
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_session),
        _permission_check: None = Depends(
            RoleChecker(form_name=FormName.PATIENT, required_permission=PermissionAction.VIEW)),
) -> Any:
    """
    دریافت تاریخ هایی که در ان بیمار منتظر مشاوره است.
    """

    statement = (
        select(func.cast(Patient.updated_at, Date))
        .where(Patient.patient_status == PatientStatus.AWAITING_CONSULTATION)
        .distinct()
        .order_by(func.cast(Patient.updated_at, Date).desc())
    )
    results = await session.exec(statement)
    db_dates = results.all()

    if not db_dates:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="no Patient waiting for consultation")


    return WaitingForConsultantDatesResponse(dates=db_dates)
# ---------------------------------------------------------------------------

@router.get("/awaiting-for-consultation-by-date/{target_date}", response_model=AwaitingForConsultationPatientsResponse)
async def get_awaiting_for_consultation_by_date(
        *,
        current_user: User = Depends(get_current_active_user),
        _permission_check: None = Depends(
            RoleChecker(form_name=FormName.MESSAGE, required_permission=PermissionAction.VIEW)),
        target_date : date,
        session: AsyncSession = Depends(get_session),
) -> Any:
    """
برای دریافت تاریخ هایی که در ان پیام نخانده شده وجود دارد
    """
    statement = (
        select(Patient.telegram_id, Patient.full_name)

        # اعمال فیلترها
        .where(Patient.patient_status == PatientStatus.AWAITING_CONSULTATION)
        .where(func.cast(Patient.updated_at, Date) == target_date)
        # گروه‌بندی برای اطمینان از نتایج منحصر به فرد برای هر بیمار
        .group_by(Patient.telegram_id, Patient.full_name)
    )
    results = await session.exec(statement)

    # 3. دریافت تمام نتایج به صورت یک لیست
    #    .all() در اینجا لیستی از تاریخ‌ها را برمی‌گرداند

    # 4. برگرداندن نتیجه در قالب schema تعریف شده
    return AwaitingForConsultationPatientsResponse(patients=results)



@router.get("/by-id/{patient_id}", response_model=PatientRead)
async def read_patient(
        *,
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_session),
        _permission_check: None = Depends(
            RoleChecker(form_name=FormName.PATIENT, required_permission=PermissionAction.VIEW)),
        patient_id: int
) -> Patient:
    """
    دریافت اطلاعات یک بیمار خاص با استفاده از شناسه (ID).
    """
    statement = select(Patient).where(Patient.patient_id == patient_id)

    db_patient = (await session.exec(statement)).one_or_none()

    if not db_patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    return db_patient
