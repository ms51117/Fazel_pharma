# app/routes/drug_map.py

from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from database import get_session
from app.models.drug_map import DrugMap
from app.models.drug import Drug
from app.models.disease_type import DiseaseType
from app.schemas.drug_map import DrugMapCreate, DrugMapRead

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=DrugMapRead)
async def create_drug_disease_mapping(
        *,
        session: AsyncSession = Depends(get_session),
        mapping_in: DrugMapCreate,
) -> Any:
    """
    ایجاد یک ارتباط جدید بین یک دارو و یک نوع بیماری.
    """
    # 1. بررسی وجود دارو
    drug = await session.get(Drug, mapping_in.drugs_id)
    if not drug:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Drug with ID {mapping_in.drugs_id} not found."
        )

    # 2. بررسی وجود نوع بیماری
    disease_type = await session.get(DiseaseType, mapping_in.diseases_type_id)
    if not disease_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"DiseaseType with ID {mapping_in.diseases_type_id} not found."
        )

    # 3. ایجاد آبجکت و ذخیره
    db_mapping = DrugMap.model_validate(mapping_in)
    session.add(db_mapping)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This mapping between drug and disease type already exists."
        )
    await session.refresh(db_mapping)
    return db_mapping


@router.get("/", response_model=List[DrugMapRead])
async def read_mappings(
        *,
        session: AsyncSession = Depends(get_session),
        skip: int = 0,
        limit: int = 100,
) -> Any:
    """
    دریافت لیست تمام ارتباطات دارو-بیماری.
    """
    statement = select(DrugMap).offset(skip).limit(limit)
    mappings = (await session.exec(statement)).all()
    return mappings


@router.delete("/", status_code=status.HTTP_200_OK)
async def delete_drug_disease_mapping(
        *,
        session: AsyncSession = Depends(get_session),
        mapping_to_delete: DrugMapCreate,  # از اسکیمای Create برای دریافت drug_id و disease_type_id استفاده می‌کنیم
):
    """
    حذف یک ارتباط مشخص بین دارو و بیماری.
    """
    mapping = await session.get(
        DrugMap,
        (mapping_to_delete.diseases_type_id, mapping_to_delete.drugs_id)
    )

    if not mapping:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mapping not found."
        )

    await session.delete(mapping)
    await session.commit()
    return {"ok": True, "message": "Mapping deleted successfully"}
