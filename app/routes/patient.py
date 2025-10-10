# In file: app/routes/patient.py

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select, or_
from typing import List

# برای استفاده از AsyncSession، باید آن را از کتابخانه مربوطه import کنید
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.permission import FormName, PermissionAction, RoleChecker
# مسیر get_session باید به نسخه async اشاره کند
from database import get_session
from app.models.patient import Patient
from app.schemas.patient import PatientCreate, PatientRead, PatientUpdate
from security import get_current_active_user
from app.models.user import User

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
            Patient.mobile_number == patient_in.mobile_number,
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
@router.get("/{patient_id}", response_model=PatientRead)
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
    db_patient = await session.get(Patient, patient_id)
    if not db_patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    return db_patient


# ===================================================================
# 4. UPDATE A PATIENT
# ===================================================================
@router.patch("/{patient_id}", response_model=PatientRead)
async def update_patient(
        *,
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_session),
        _permission_check: None = Depends(
            RoleChecker(form_name=FormName.PATIENT, required_permission=PermissionAction.UPDATE)),
        patient_id: int,
        patient_in: PatientUpdate
) -> Patient:
    """
    به‌روزرسانی اطلاعات یک بیمار.
    فقط فیلدهایی که در درخواست ارسال شوند، آپدیت خواهند شد.
    """
    db_patient = await session.get(Patient, patient_id)
    if not db_patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    # استراتژی آپدیت مشابه فایل user.py
    # تبدیل داده‌های ورودی به دیکشنری و حذف مقادیر None یا ارسال نشده
    update_data = patient_in.model_dump(exclude_unset=True)

    # به‌روزرسانی فیلدهای مدل با داده‌های جدید
    for key, value in update_data.items():
        setattr(db_patient, key, value)

    session.add(db_patient)
    await session.commit()
    await session.refresh(db_patient)

    return db_patient


# ===================================================================
# 5. DELETE A PATIENT
# ===================================================================
@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_patient(
        *,
        current_user: User = Depends(get_current_active_user),
        _permission_check: None = Depends(
            RoleChecker(form_name=FormName.PATIENT, required_permission=PermissionAction.DELETE)),

        session: AsyncSession = Depends(get_session),
        patient_id: int
) -> None:
    """
    حذف یک بیمار از سیستم.
    """
    db_patient = await session.get(Patient, patient_id)
    if not db_patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    await session.delete(db_patient)
    await session.commit()

    # طبق استاندارد RESTful، پس از حذف موفق، پاسخی با status_code 204 و بدون بدنه برمیگردانیم.
    return None
