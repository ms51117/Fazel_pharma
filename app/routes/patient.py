# app/routers/patient.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List

# Import models, schemas, and dependencies
from app.models.patient import Patient
from app.schemas.patient import PatientCreate, PatientRead, PatientUpdate
from database import get_session

# Create an API router for patient-related endpoints
router = APIRouter()

@router.post("/", response_model=PatientRead, status_code=status.HTTP_201_CREATED)
async def create_patient(
    *,
    session: AsyncSession = Depends(get_session),
    patient_in: PatientCreate
):
    """
    Create a new patient in the database.
    """
    # Check if a patient with the same national_code already exists
    if patient_in.national_code:
        existing_patient = await session.exec(select(Patient).where(Patient.national_code == patient_in.national_code))
        if existing_patient.first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A patient with this national code already exists."
            )

    # Check if a patient with the same mobile_number already exists
    if patient_in.mobile_number:
        existing_patient = await session.exec(select(Patient).where(Patient.mobile_number == patient_in.mobile_number))
        if existing_patient.first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A patient with this mobile number already exists."
            )

    # Create the Patient DB model instance
    patient_data = patient_in.dict(exclude_unset=True)
    db_patient_obj = Patient(**patient_data)

    # Add the new patient to the session and commit to the database
    session.add(db_patient_obj)
    await session.commit()
    await session.refresh(db_patient_obj)

    return db_patient_obj

@router.get("/{patient_id}", response_model=PatientRead)
async def read_patient_by_id(
    patient_id: int,
    session: AsyncSession = Depends(get_session)
):
    """
    Retrieve a patient by their ID.
    """
    patient = await session.get(Patient, patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {patient_id} not found."
        )
    return patient

@router.get("/", response_model=List[PatientRead])
async def read_patients(
    session: AsyncSession = Depends(get_session)
):
    """
    Retrieve a list of all patients.
    """
    patients = await session.exec(select(Patient))
    return patients.all()

@router.patch("/{patient_id}", response_model=PatientRead)
async def update_patient(
    patient_id: int,
    patient_in: PatientUpdate,
    session: AsyncSession = Depends(get_session)
):
    """
    Update an existing patient's information.
    """
    patient_instance = await session.get(Patient, patient_id)
    if not patient_instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {patient_id} not found."
        )

    # Check for duplicate national_code, mobile_number
    if patient_in.national_code:
        existing_patient = await session.exec(select(Patient).where(Patient.national_code == patient_in.national_code))
        if existing_patient.first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A patient with this national code already exists."
            )

    if patient_in.mobile_number:
        existing_patient = await session.exec(select(Patient).where(Patient.mobile_number == patient_in.mobile_number))
        if existing_patient.first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A patient with this mobile number already exists."
            )

    # Update patient data
    for key, value in patient_in.dict(exclude_unset=True).items():
        setattr(patient_instance, key, value)

    session.add(patient_instance)
    await session.commit()
    await session.refresh(patient_instance)

    return patient_instance

@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_patient(
    patient_id: int,
    session: AsyncSession = Depends(get_session)
):
    """
    Delete a patient by their ID.
    """
    patient = await session.get(Patient, patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {patient_id} not found."
        )

    await session.delete(patient)
    await session.commit()

    return None
