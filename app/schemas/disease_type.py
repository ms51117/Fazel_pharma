# app/schemas/disease_type_schema.py

from typing import Optional
from sqlmodel import SQLModel, Field

# ---------------------------------------------------------------------------
# 1. اسکیمای پایه
# ---------------------------------------------------------------------------
class DiseaseTypeBase(SQLModel):
    disease_name: str = Field(max_length=100, unique=True, index=True, description="Name of the disease type")

# ---------------------------------------------------------------------------
# 2. اسکیمای ایجاد (Create)
# ---------------------------------------------------------------------------
class DiseaseTypeCreate(DiseaseTypeBase):
    pass

# ---------------------------------------------------------------------------
# 3. اسکیمای خواندن (Read)
# ---------------------------------------------------------------------------
class DiseaseTypeRead(DiseaseTypeBase):
    disease_type_id: int

# ---------------------------------------------------------------------------
# 4. اسکیمای آپدیت (Update)
# ---------------------------------------------------------------------------
class DiseaseTypeUpdate(SQLModel):
    disease_name: Optional[str] = None
