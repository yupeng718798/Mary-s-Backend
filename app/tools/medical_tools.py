from sqlalchemy.orm import Session
from app.models.medical import MedicalRecord, MedicalAnalysis
from app.models.profile import Profile
from app.models.medication import Medication, SymptomDiary
from app.models.consultation import Consultation
from app.services.ai_agent import medical_analysis as ai_medical_analysis


def get_medical_records(db: Session, user_id: str, limit: int = 10) -> list[dict]:
    records = (
        db.query(MedicalRecord)
        .filter(MedicalRecord.user_id == user_id)
        .order_by(MedicalRecord.upload_date.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": str(r.id),
            "title": r.title,
            "record_type": r.record_type,
            "status": r.status,
            "upload_date": r.upload_date.isoformat() if r.upload_date else None,
        }
        for r in records
    ]


def get_medical_analysis(db: Session, record_id: str) -> dict | None:
    analysis = (
        db.query(MedicalAnalysis)
        .filter(MedicalAnalysis.record_id == record_id)
        .first()
    )
    if not analysis:
        return None
    return {
        "id": str(analysis.id),
        "record_id": str(analysis.record_id),
        "summary": analysis.summary,
        "risk_level": analysis.risk_level,
        "agent_name": analysis.agent_name,
        "created_at": analysis.created_at.isoformat() if analysis.created_at else None,
    }


def analyze_medical_record(db: Session, record_id: str) -> dict:
    record = db.query(MedicalRecord).filter(MedicalRecord.id == record_id).first()
    if not record:
        return {"error": "Record not found"}

    title = record.title or ""
    record_type = record.record_type or ""
    text_for_analysis = f"病历标题: {title}\n类型: {record_type}\n内容: {title}"

    result = ai_medical_analysis(text_for_analysis)

    analysis = MedicalAnalysis(
        record_id=record.id,
        summary=result.get("summary", ""),
        risk_level=result.get("risk_level", "unknown"),
        agent_name="Medical Analysis Agent",
    )
    db.add(analysis)

    record.status = "analyzed"
    db.commit()
    db.refresh(analysis)

    return {
        "id": str(analysis.id),
        "summary": analysis.summary,
        "risk_level": analysis.risk_level,
        "agent_name": analysis.agent_name,
    }


def get_profile(db: Session, user_id: str) -> dict | None:
    profile = db.query(Profile).filter(Profile.id == user_id).first()
    if not profile:
        return None
    return {
        "id": str(profile.id),
        "full_name": profile.full_name,
        "date_of_birth": profile.date_of_birth.isoformat() if profile.date_of_birth else None,
        "gender": profile.gender,
        "phone": profile.phone,
        "emergency_contact": profile.emergency_contact,
        "language": profile.language,
    }


def get_medications(db: Session, user_id: str) -> list[dict]:
    meds = (
        db.query(Medication)
        .filter(Medication.user_id == user_id)
        .order_by(Medication.created_at.desc())
        .all()
    )
    return [
        {
            "id": str(m.id),
            "medicine_name": m.medicine_name,
            "dosage": m.dosage,
            "frequency": m.frequency,
            "reminder_time": str(m.reminder_time) if m.reminder_time else None,
            "note": m.note,
        }
        for m in meds
    ]


def add_medication(db: Session, user_id: str, medicine_name: str, dosage: str, frequency: str) -> dict:
    med = Medication(
        user_id=user_id,
        medicine_name=medicine_name,
        dosage=dosage,
        frequency=frequency,
    )
    db.add(med)
    db.commit()
    db.refresh(med)
    return {
        "id": str(med.id),
        "medicine_name": med.medicine_name,
        "dosage": med.dosage,
        "frequency": med.frequency,
    }


def get_symptom_diary(db: Session, user_id: str, limit: int = 10) -> list[dict]:
    entries = (
        db.query(SymptomDiary)
        .filter(SymptomDiary.user_id == user_id)
        .order_by(SymptomDiary.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": str(e.id),
            "symptom": e.symptom,
            "severity": e.severity,
            "mood": e.mood,
            "notes": e.notes,
            "created_at": e.created_at.isoformat() if e.created_at else None,
        }
        for e in entries
    ]


def get_consultations(db: Session, user_id: str, limit: int = 10) -> list[dict]:
    cons = (
        db.query(Consultation)
        .filter(Consultation.user_id == user_id)
        .order_by(Consultation.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": str(c.id),
            "symptoms": c.symptoms,
            "ai_questions": c.ai_questions,
            "status": c.status,
            "created_at": c.created_at.isoformat() if c.created_at else None,
        }
        for c in cons
    ]


TOOL_REGISTRY = {
    "get_medical_records": get_medical_records,
    "get_medical_analysis": get_medical_analysis,
    "analyze_medical_record": analyze_medical_record,
    "get_profile": get_profile,
    "get_medications": get_medications,
    "add_medication": add_medication,
    "get_symptom_diary": get_symptom_diary,
    "get_consultations": get_consultations,
}
