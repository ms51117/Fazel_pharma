# app/models/patient.py

from typing import Optional, TYPE_CHECKING, List
from sqlmodel import Field, Relationship, SQLModel, JSON

from app.models.base import BaseDates
from sqlalchemy import Column
from sqlalchemy.types import Enum as SQLAlchemyEnum # ایمپورت Enum از SQLAlchemy
from app.models.base import Base
import sqlalchemy as sa


import enum

if TYPE_CHECKING:
    from app.models.order import order
    from app.models.order import Order
    from app.models.message import Message



class GenderEnum(str, enum.Enum):
    """
    Enumeration for gender.
    Values are stored as strings in the database.
    """
    MALE = "male"
    FEMALE = "female"
    UNKNOWN = "unknown"

class PatientBase(SQLModel):
    """Base model for Patient shared properties"""
    full_name: str = Field(
        max_length=50,
        nullable=False,
        description="Full name"
    )

    sex: Optional[GenderEnum] = Field(
        default=GenderEnum.UNKNOWN,
        nullable=False,
        description="sex of patient"
    )



    age: Optional[int] = Field(
        default=None,
        description="Age in years"
    )
    weight: Optional[float] = Field(
        default=None,
        description="Weight in kg"
    )
    height: Optional[float] = Field(
        default=None,
        description="Height in cm"
    )
    mobile_number: Optional[str] = Field(
        default=None,
        max_length=11,
        description="Mobile number"
    )
    postal_code: Optional[str] = Field(
        default=None,
        max_length=10,
        description="Postal code"
    )
    address: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Physical address"
    )
    telegram_id: Optional[str] = Field(
        default=None,
        max_length=100,
        index=True,
        description="Telegram ID"
    )
    specific_diseases: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Specific diseases or conditions"
    )
    consultant_type: Optional[str] = Field(
        default=None,
        description="consultant type"
    )
    special_conditions: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Specific conditions"
    )
    photo_paths: Optional[List[str]] = Field(
        sa_column=Column(JSON),
        default=[],
        description="photo_paths"
    )




class Patient(PatientBase, BaseDates, table=True):
    """Database model for Patient table (tbl_Patient)"""
    __tablename__ = "tbl_Patient"

    patient_id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Auto-incremented patient ID"
    )

    # Relationships
    order: List["Order"] = Relationship(back_populates="patient")
    messages: Optional["Message"] = Relationship(back_populates="patient")
