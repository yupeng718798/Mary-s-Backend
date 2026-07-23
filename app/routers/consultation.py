from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from app.database.connection import get_db
from app.models.consultation import Consultation
from app.schemas.consultation import ConsultationCreate, ConsultationUpdate, ConsultationResponse
from app.services.ai_agent import consultation_analysis as run_consultation_analysis

router = APIRouter(prefix="/api/consultation", tags=["Consultation"])


@router.post("/create", response_model=ConsultationResponse)
def create_consultation(data: ConsultationCreate, db: Session = Depends(get_db)):
    ai_questions = run_consultation_analysis(data.symptoms)
    consultation = Consultation(
        user_id=data.user_id,
        symptoms=data.symptoms,
        ai_questions=ai_questions,
        status="preparing",
    )
    db.add(consultation)
    db.commit()
    db.refresh(consultation)
    return consultation


@router.get("/{user_id}", response_model=list[ConsultationResponse])
def get_consultations(user_id: UUID, db: Session = Depends(get_db)):
    return db.query(Consultation).filter(Consultation.user_id == user_id).all()


@router.put("/{consultation_id}", response_model=ConsultationResponse)
def update_consultation(consultation_id: UUID, data: ConsultationUpdate, db: Session = Depends(get_db)):
    consultation = db.query(Consultation).filter(Consultation.id == consultation_id).first()
    if not consultation:
        raise HTTPException(status_code=404, detail="Consultation not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(consultation, key, value)
    db.commit()
    db.refresh(consultation)
    return consultation
