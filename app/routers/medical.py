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
from app.services.ocr_service import extract_text
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
        # File type validation
        allowed_types = ["image/jpeg", "image/jpg", "image/png"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file.content_type}. Only .jpg, .jpeg, .png images are supported."
            )
        
        # Save file
        filename = f"{uuid.uuid4()}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as f:
            f.write(file.file.read())
        file_url = file_path

    # Create medical record
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
    
    # If image file exists, perform OCR and AI analysis
    if file_url and os.path.exists(file_url):
        try:
            # 1. OCR text extraction
            extracted_text = extract_text(file_url)
            
            # 2. AI analysis
            if extracted_text and not extracted_text.startswith("["):
                analysis_prompt = (
                    f"A patient has uploaded a medical image report.\n"
                    f"File name: {title}\n"
                    f"File type: {record_type or 'Medical image'}\n\n"
                    f"Extracted text content:\n{extracted_text[:3000]}\n\n"
                    f"Please analyze the above content and provide:\n"
                    f"1. Brief summary (2-3 sentences)\n"
                    f"2. Risk level: low/medium/high\n"
                    f"3. Key details or recommendations to note"
                )
            else:
                analysis_prompt = (
                    f"A patient has uploaded a medical image report.\n"
                    f"File name: {title}\n"
                    f"OCR extraction result: {extracted_text or 'Unable to extract text'}\n"
                    f"Please note this is a preliminary analysis based on the file name. Recommend the patient review the actual report."
                )
            
            ai_result = run_medical_analysis(analysis_prompt)
            
            # 3. Save analysis results (including OCR text)
            analysis = MedicalAnalysis(
                record_id=record.id,
                extracted_text=extracted_text,
                agent_name="Medical Analysis Agent",
                summary=ai_result.get("summary", ""),
                risk_level=ai_result.get("risk_level", "unknown"),
            )
            db.add(analysis)
            record.status = "analyzed"
            db.commit()
            
        except Exception as e:
            # If OCR or analysis fails, log the error but don't block the upload
            print(f"OCR or AI analysis failed: {str(e)}")
            pass
    
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

    # Try to extract file content
    extracted = ""
    if record.file_url and os.path.exists(record.file_url):
        extracted = extract_text(record.file_url)

    if extracted and not extracted.startswith("["):
        text = (
            f"A patient has uploaded a medical file.\n"
            f"File name: {record.title}\n"
            f"File type: {record.record_type or 'General checkup'}\n"
            f"Extracted text content:\n{extracted[:3000]}\n\n"
            f"Please analyze the above content and provide:\n"
            f"1. Brief summary (2-3 sentences)\n"
            f"2. Risk level: low/medium/high\n"
            f"3. Key details or recommendations to note"
        )
    else:
        text = (
            f"A patient has uploaded a medical file.\n"
            f"File name: {record.title}\n"
            f"File type: {record.record_type or 'General checkup'}\n"
            f"File content extraction result: {extracted or 'Unable to extract'}\n"
            f"Based on the file name and type, provide possible test descriptions, common indicator interpretations, and general health advice.\n"
            f"If unable to determine specific content, note this is a preliminary analysis and recommend the patient review the actual report."
        )

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


@router.delete("/{record_id}")
def delete_record(record_id: UUID, db: Session = Depends(get_db)):
    record = db.query(MedicalRecord).filter(MedicalRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    # Delete associated analyses first
    db.query(MedicalAnalysis).filter(MedicalAnalysis.record_id == record_id).delete()

    # Remove the uploaded file if it exists
    if record.file_url and os.path.exists(record.file_url):
        try:
            os.remove(record.file_url)
        except Exception:
            pass

    db.delete(record)
    db.commit()
    return {"message": "Record deleted"}


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