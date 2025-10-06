# app/schemas/patient.py

from sqlmodel import SQLModel
from datetime import datetime
from typing import Optional

class PatientCreate(SQLModel):
    """
    Schema for creating a new patient. This is what the API expects as input.
    """
    full_name: str
    national_code: Optional[str] = None
    mobile_number: Optional[str] = None
    address: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    consultant_id: Optional[int] = None

class PatientRead(PatientCreate):
    """
    Schema for reading patient data. This is what the API returns as output.
    """
    patient_id: int
    created_at: datetime
    updated_at: datetime

class PatientUpdate(SQLModel):
    """
    Schema for updating a patient's information. All fields are optional.
    """
    full_name: Optional[str] = None
    national_code: Optional[str] = None
    mobile_number: Optional[str] = None
    address: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    consultant_id: Optional[int] = None
