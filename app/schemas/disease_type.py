# app/schemas/disease_type_schema.py

from typing import Optional
from sqlmodel import SQLModel, Field
from app.models.disease_type import DiseaseTypeBase

# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# 2. اسکیمای ایجاد (Create)
# ---------------------------------------------------------------------------
class DiseaseTypeCreate(DiseaseTypeBase):
    pass

# ---------------------------------------------------------------------------
# 3. اسکیمای خواندن (Read)
# ---------------------------------------------------------------------------
class DiseaseTypeRead(DiseaseTypeBase):
    diseases_type_id: int

# ---------------------------------------------------------------------------
# 4. اسکیمای آپدیت (Update)
# ---------------------------------------------------------------------------
class DiseaseTypeUpdate(SQLModel):
    disease_name: Optional[str] = None
    diseases_explain: Optional[str] = None
