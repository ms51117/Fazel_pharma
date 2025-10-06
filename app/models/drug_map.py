# app/models/drug_map.py

from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel
from app.models.base import BaseDates

if TYPE_CHECKING:
    from app.models.disease_type import DiseaseType
    from app.models.drug import Drug


class DrugMapBase(SQLModel):
    """Base model for DrugMap shared properties"""
    diseases_type_id: int = Field(
        # foreign_key="tbl_DiseaseType.diseases_type_id",
        nullable=False,
        description="Disease type ID"
    )
    drugs_id: int = Field(
        # foreign_key="tbl_drug.drugs_id",
        nullable=False,
        description="Drug ID"
    )


class DrugMap(DrugMapBase, BaseDates, table=True):
    """Database model for DrugMap table (tbl_DrugMap)"""
    __tablename__ = "tbl_DrugMap"

    drugs_map_id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Auto-incremented drug map ID"
    )

    # Relationships
    # disease_type: "DiseaseType" = Relationship(back_populates="drug_maps")
    # drug: "Drug" = Relationship(back_populates="drug_maps")
