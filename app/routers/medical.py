from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from uuid import UUID
from app.database.connection import get_db
from app.models.medical import MedicalRecord, MedicalAnalysis, GeneratedReport
from app.schemas.medical import (
    MedicalRecordCreate, MedicalRecordResponse,
    MedicalAnalysisResponse, ReportCreate, ReportResponse
)
from app.services.ai_agent import medical_analysis as run_medical_analysis
import os
import uuid

router = APIRouter(prefix="/api/medical", tags=["Medical"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload", response_model=MedicalRecordResponse)
def upload_record(
    user_id: UUID = Form(...),
    record_type: str = Form(...),
    title: str = Form(...),
    file: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    file_url = None
    if file:
        filename = f"{uuid.uuid4()}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as f:
            f.write(file.file.read())
        file_url = file_path

    record = MedicalRecord(
        user_id=user_id,
        title=title,
        record_type=record_type,
        file_url=file_url,
        status="uploaded",
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/records/{user_id}", response_model=list[MedicalRecordResponse])
def get_records(user_id: UUID, db: Session = Depends(get_db)):
    return db.query(MedicalRecord).filter(MedicalRecord.user_id == user_id).all()


@router.get("/analyze/{record_id}", response_model=list[MedicalAnalysisResponse])
def get_analyses(record_id: UUID, db: Session = Depends(get_db)):
    return db.query(MedicalAnalysis).filter(MedicalAnalysis.record_id == record_id).all()


@router.post("/analyze/{record_id}", response_model=MedicalAnalysisResponse)
def analyze_record(record_id: UUID, db: Session = Depends(get_db)):
    record = db.query(MedicalRecord).filter(MedicalRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    text = f"Title: {record.title}. Type: {record.record_type or 'general'}."
    result = run_medical_analysis(text)

    analysis = MedicalAnalysis(
        record_id=record_id,
        agent_name="Medical Analysis Agent",
        summary=result.get("summary", ""),
        risk_level=result.get("risk_level", "unknown"),
    )
    db.add(analysis)
    record.status = "analyzed"
    db.commit()
    db.refresh(analysis)
    return analysis


@router.get("/{record_id}", response_model=MedicalRecordResponse)
def get_record(record_id: UUID, db: Session = Depends(get_db)):
    record = db.query(MedicalRecord).filter(MedicalRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record


@router.post("/report/generate", response_model=ReportResponse)
def generate_report(data: ReportCreate, db: Session = Depends(get_db)):
    record = db.query(MedicalRecord).filter(MedicalRecord.id == data.record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    report = GeneratedReport(
        user_id=data.user_id,
        report_type=data.report_type or "general",
        content="Medical report generated - placeholder for AI-generated content.",
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


@router.get("/report/{user_id}", response_model=list[ReportResponse])
def get_reports(user_id: UUID, db: Session = Depends(get_db)):
    return db.query(GeneratedReport).filter(GeneratedReport.user_id == user_id).all()
