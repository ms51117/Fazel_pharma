# app/schemas/drug_schema.py

from typing import Optional, List
from sqlmodel import SQLModel, Field
from decimal import Decimal

# Import اسکیمای DiseaseType برای استفاده در خروجی
from app.schemas.disease_type import DiseaseTypeRead
from app.models.drug import DrugBase


# ---------------------------------------------------------------------------
# 1. اسکیمای پایه دارو (Drug)
# ---------------------------------------------------------------------------
# class DrugBase(SQLModel):
#     drugs_name_fa: str = Field(max_length=200, index=True, description="Persian name of the drug")
#     drugs_name_en: str = Field(max_length=200, index=True, description="English name of the drug")
#     drugs_price: Decimal = Field(max_digits=12, decimal_places=0, description="Price of the drug")
#     drugs_description: Optional[str] = Field(default=None, max_length=1000, description="Description of the drug")
#
#     # کلید خارجی به جدول DiseaseType
#     # این فیلد در زمان ایجاد و آپدیت ضروری است
#     diseases_type_id: int = Field(foreign_key="tbl_DiseaseType.diseases_type_id")


# ---------------------------------------------------------------------------
# 2. اسکیمای ایجاد (Create)
# ---------------------------------------------------------------------------
class DrugCreate(DrugBase):
    pass


# ---------------------------------------------------------------------------
# 3. اسکیمای آپدیت (Update)
# ---------------------------------------------------------------------------
class DrugUpdate(SQLModel):
    drugs_name_fa: Optional[str] = None
    drugs_name_en: Optional[str] = None
    drugs_price: Optional[Decimal] = None
    drugs_description: Optional[str] = None
    diseases_type_id: Optional[int] = None


# ---------------------------------------------------------------------------
# 4. اسکیمای پایه برای خواندن (Read) - بدون روابط
# ---------------------------------------------------------------------------
class DrugRead(DrugBase):
    drugs_id: int


