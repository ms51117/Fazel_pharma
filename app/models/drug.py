# app/models/drug.py

from typing import Optional, TYPE_CHECKING, List
from sqlmodel import Field, Relationship, SQLModel
from decimal import Decimal
from app.models.base import BaseDates

from app.models.drug_map import DrugMap

if TYPE_CHECKING:
    from app.models.order_list import OrderList
    from app.models.disease_type import DiseaseType


class DrugBase(SQLModel):
    """Base model for Drug shared properties"""
    drug_pname: str = Field(
        max_length=200,
        nullable=False,
        description="Drug Persian name"
    )
    drug_lname: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Drug Latin/English name"
    )
    drug_explain: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Drug explanation/description"
    )
    drug_how_to_use: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Instructions for use"
    )
    unit: str = Field(
        max_length=50,
        nullable=False,
        description="Unit of measurement"
    )
    price: Decimal = Field(
        default=0,
        max_digits=12,
        decimal_places=0,
        description="Price in Rials"
    )


class Drug(DrugBase, BaseDates, table=True):
    """Database model for Drug table (tbl_drug)"""
    __tablename__ = "tbl_Drug"

    drugs_id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Auto-incremented drug ID"
    )

    # Relationships
    order_list: List["OrderList"] = Relationship(back_populates="drug")
    disease_type: list["DiseaseType"] = Relationship(back_populates="drug", link_model=DrugMap)
    def __str__(self) -> str:
        """
        این متد به پایتون و sqladmin می‌گوید که هرگاه خواستید یک نمونه
        از این کلاس را به صورت رشته نمایش دهید، فقط مقدار role_name را برگردانید.
        """
        return self.drug_lname

