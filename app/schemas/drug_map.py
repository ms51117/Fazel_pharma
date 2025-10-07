# app/schemas/drug_map_schema.py

from sqlmodel import SQLModel, Field

# ---------------------------------------------------------------------------
# 1. اسکیمای پایه و ورودی برای ایجاد ارتباط (CREATE)
# ---------------------------------------------------------------------------
class DrugMapBase(SQLModel):
    diseases_type_id: int = Field(
        description="ID of the disease type to map",
        foreign_key="tbl_DiseaseType.diseases_type_id",
        primary_key=True
    )
    drugs_id: int = Field(
        description="ID of the drug to map",
        foreign_key="tbl_Drug.drugs_id",
        primary_key=True
    )

class DrugMapCreate(DrugMapBase):
    pass

# ---------------------------------------------------------------------------
# 2. اسکیمای خروجی برای نمایش ارتباط (READ)
# ---------------------------------------------------------------------------
class DrugMapRead(DrugMapBase):
    # این اسکیما دقیقاً مانند پایه است چون کلیدهای خارجی خودشان داده‌های اصلی هستند.
    pass

# نکته: اسکیمای آپدیت برای این مدل معنی ندارد، چون برای تغییر یک ارتباط،
# باید رکورد فعلی را حذف و رکورد جدیدی ایجاد کرد.
