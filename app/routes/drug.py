# app/routes/drug.py

from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.permission import FormName, PermissionAction, RoleChecker
from database import get_session
from app.models.drug import Drug
from app.models.disease_type import DiseaseType  # برای اعتبارسنجی
from app.schemas.drug import DrugCreate, DrugRead, DrugUpdate, DrugReadWithDetails
from security import get_current_active_user
from app.models.user import User

router = APIRouter()


async def get_disease_type_or_404(disease_type_id: int, session: AsyncSession):
    """Helper function to check if DiseaseType exists."""
    disease_type = await session.get(DiseaseType, disease_type_id)
    if not disease_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"DiseaseType with ID {disease_type_id} not found."
        )
    return disease_type


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=DrugRead)
async def create_drug(
        *,
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_session),
        _permission_check: None = Depends(
            RoleChecker(form_name=FormName.DRUG, required_permission=PermissionAction.INSERT)),
        drug_in: DrugCreate,
) -> Any:
    """
    ایجاد یک داروی جدید.
    """
    # 1. اعتبارسنجی وجود `diseases_type_id`
    await get_disease_type_or_404(drug_in.diseases_type_id, session)

    # 2. ایجاد آبجکت دارو و ذخیره
    db_drug = Drug.model_validate(drug_in)
    session.add(db_drug)
    await session.commit()
    await session.refresh(db_drug)
    return db_drug


@router.get("/", response_model=List[DrugReadWithDetails])
async def read_drugs(
        *,
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_session),
        _permission_check: None = Depends(
            RoleChecker(form_name=FormName.DRUG, required_permission=PermissionAction.VIEW)),

        skip: int = 0,
        limit: int = 100,
) -> Any:
    """
    دریافت لیست داروها همراه با اطلاعات نوع بیماری.
    """
    statement = select(Drug).options(selectinload(Drug.disease_type)).offset(skip).limit(limit)
    drugs = (await session.exec(statement)).all()
    return drugs


@router.get("/{drug_id}", response_model=DrugReadWithDetails)
async def read_drug_by_id(
        *,
        current_user: User = Depends(get_current_active_user),
        _permission_check: None = Depends(
            RoleChecker(form_name=FormName.DRUG, required_permission=PermissionAction.VIEW)),

        drug_id: int,
        session: AsyncSession = Depends(get_session),
) -> Any:
    """
    دریافت اطلاعات یک دارو با شناسه (ID) به همراه نوع بیماری.
    """
    statement = select(Drug).where(Drug.drugs_id == drug_id).options(selectinload(Drug.disease_type))
    drug = (await session.exec(statement)).one_or_none()

    if not drug:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Drug with ID {drug_id} not found",
        )
    return drug


@router.patch("/{drug_id}", response_model=DrugRead)
async def update_drug(
        *,
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_session),
        _permission_check: None = Depends(
            RoleChecker(form_name=FormName.DRUG, required_permission=PermissionAction.UPDATE)),

        drug_id: int,
        drug_in: DrugUpdate,
) -> Any:
    """
    آپدیت اطلاعات یک دارو.
    """
    db_drug = await session.get(Drug, drug_id)
    if not db_drug:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Drug with ID {drug_id} not found",
        )

    update_data = drug_in.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No data to update")

    # اگر diseases_type_id در حال آپدیت بود، وجود آن را چک کن
    if "diseases_type_id" in update_data:
        await get_disease_type_or_404(update_data["diseases_type_id"], session)

    db_drug.sqlmodel_update(update_data)
    session.add(db_drug)
    await session.commit()
    await session.refresh(db_drug)
    return db_drug


@router.delete("/{drug_id}")
async def delete_drug(
        *,
        current_user: User = Depends(get_current_active_user),
        _permission_check: None = Depends(
            RoleChecker(form_name=FormName.DRUG, required_permission=PermissionAction.DELETE)),

        drug_id: int,
        session: AsyncSession = Depends(get_session),
):
    """
    حذف یک دارو.
    """
    drug = await session.get(Drug, drug_id)
    if not drug:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Drug with ID {drug_id} not found",
        )

    await session.delete(drug)
    await session.commit()
    return {"ok": True, "message": "Drug deleted successfully"}
