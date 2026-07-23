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

    # 尝试提取文件内容
    extracted = ""
    if record.file_url and os.path.exists(record.file_url):
        extracted = extract_text(record.file_url)

    if extracted and not extracted.startswith("["):
        text = (
            f"患者上传了一份医疗文件。"
            f"文件名: {record.title}. "
            f"文件类型: {record.record_type or '一般检查'}. "
            f"提取的文本内容:\n{extracted[:3000]}\n\n"
            f"请基于上述内容进行分析，提供："
            f"1. 简短摘要（2-3句话）"
            f"2. 风险等级：low/medium/high"
            f"3. 需要注意的关键细节或建议"
        )
    else:
        text = (
            f"患者上传了一份医疗文件。"
            f"文件名: {record.title}. "
            f"文件类型: {record.record_type or '一般检查'}. "
            f"文件内容提取结果: {extracted or '无法提取'}. "
            f"请基于文件名和类型，给出可能的检查项目说明、常见指标解读，以及一般性的健康建议。"
            f"如果无法确定具体内容，请说明这是基于文件名的初步分析，建议患者查看实际报告。"
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
