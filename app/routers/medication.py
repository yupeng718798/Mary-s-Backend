from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from app.database.connection import get_db
from app.models.medication import Medication
from app.schemas.medication import MedicationCreate, MedicationResponse

router = APIRouter(prefix="/api/medication", tags=["Medication"])


@router.post("/add", response_model=MedicationResponse)
def add_medication(data: MedicationCreate, db: Session = Depends(get_db)):
    med = Medication(**data.model_dump())
    db.add(med)
    db.commit()
    db.refresh(med)
    return med


@router.get("/{user_id}", response_model=list[MedicationResponse])
def get_medications(user_id: UUID, db: Session = Depends(get_db)):
    return db.query(Medication).filter(Medication.user_id == user_id).all()


@router.delete("/{medication_id}")
def delete_medication(medication_id: UUID, db: Session = Depends(get_db)):
    med = db.query(Medication).filter(Medication.id == medication_id).first()
    if not med:
        raise HTTPException(status_code=404, detail="Medication not found")
    db.delete(med)
    db.commit()
    return {"message": "Medication deleted"}
