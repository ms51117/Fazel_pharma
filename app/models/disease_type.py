# app/models/disease_type.py

from typing import Optional, TYPE_CHECKING, List
from sqlmodel import Field, Relationship, SQLModel
from app.models.base import BaseDates

if TYPE_CHECKING:
    from app.models.drug_map import DrugMap


class DiseaseTypeBase(SQLModel):
    """Base model for DiseaseType shared properties"""
    diseases_name: str = Field(
        max_length=200,
        nullable=False,
        description="Disease name"
    )
    diseases_explain: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Disease explanation/description"
    )


class DiseaseType(DiseaseTypeBase, BaseDates, table=True):
    """Database model for DiseaseType table (tbl_DiseaseType)"""
    __tablename__ = "tbl_DiseaseType"

    diseases_type_id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Auto-incremented disease type ID"
    )

    # Relationships
    # drug_maps: List["DrugMap"] = Relationship(back_populates="disease_type")
