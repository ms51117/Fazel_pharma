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
    diseases_type_id: int = Field(description="The ID of the disease type this drug belongs to")



# ---------------------------------------------------------------------------
# 3. اسکیمای آپدیت (Update)
# ---------------------------------------------------------------------------
class DrugUpdate(SQLModel):
    drug_pname: Optional[str] = None
    drug_lname: Optional[str] = None
    drug_explain : Optional[str] = None
    drug_how_to_use : Optional[str] = None
    unit: Optional[str] = None
    price: Optional[Decimal] = None
    diseases_type_id: Optional[int] = None


# ---------------------------------------------------------------------------
# 4. اسکیمای پایه برای خواندن (Read) - بدون روابط
# ---------------------------------------------------------------------------
class DrugRead(DrugBase):
    drugs_id: int


