# app/routes/disease_type.py

from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from database import get_session
from app.models.disease_type import DiseaseType
from app.schemas.disease_type import DiseaseTypeCreate, DiseaseTypeRead, DiseaseTypeUpdate

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=DiseaseTypeRead)
async def create_disease_type(
        *,
        session: AsyncSession = Depends(get_session),
        disease_type_in: DiseaseTypeCreate,
) -> Any:
    """
    ایجاد یک نوع بیماری جدید.
    """
    db_disease_type = DiseaseType.model_validate(disease_type_in)
    session.add(db_disease_type)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Disease type with this name already exists.",
        )
    await session.refresh(db_disease_type)
    return db_disease_type


@router.get("/", response_model=List[DiseaseTypeRead])
async def read_disease_types(
        *,
        session: AsyncSession = Depends(get_session),
        skip: int = 0,
        limit: int = 100,
) -> Any:
    """
    دریافت لیست تمام انواع بیماری‌ها.
    """
    statement = select(DiseaseType).offset(skip).limit(limit)
    disease_types = (await session.exec(statement)).all()
    return disease_types


@router.get("/{disease_type_id}", response_model=DiseaseTypeRead)
async def read_disease_type_by_id(
        *,
        disease_type_id: int,
        session: AsyncSession = Depends(get_session),
) -> Any:
    """
    دریافت اطلاعات یک نوع بیماری با شناسه (ID).
    """
    disease_type = await session.get(DiseaseType, disease_type_id)
    if not disease_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Disease type with ID {disease_type_id} not found",
        )
    return disease_type


@router.patch("/{disease_type_id}", response_model=DiseaseTypeRead)
async def update_disease_type(
        *,
        session: AsyncSession = Depends(get_session),
        disease_type_id: int,
        disease_type_in: DiseaseTypeUpdate,
) -> Any:
    """
    آپدیت نام یک نوع بیماری.
    """
    db_disease_type = await session.get(DiseaseType, disease_type_id)
    if not db_disease_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Disease type with ID {disease_type_id} not found",
        )

    update_data = disease_type_in.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No data to update")

    db_disease_type.sqlmodel_update(update_data)
    session.add(db_disease_type)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Disease type with this name already exists.",
        )
    await session.refresh(db_disease_type)
    return db_disease_type


@router.delete("/{disease_type_id}")
async def delete_disease_type(
        *,
        disease_type_id: int,
        session: AsyncSession = Depends(get_session),
):
    """
    حذف یک نوع بیماری.
    """
    disease_type = await session.get(DiseaseType, disease_type_id)
    if not disease_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Disease type with ID {disease_type_id} not found",
        )

    await session.delete(disease_type)
    await session.commit()
    return {"ok": True, "message": "Disease type deleted successfully"}
