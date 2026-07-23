from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID
from app.database.connection import get_db
from app.models.medication import SymptomDiary, AgentLog
from app.schemas.medication import SymptomDiaryCreate, SymptomDiaryResponse, AgentLogResponse

router = APIRouter(prefix="/api/diary", tags=["Diary"])


@router.post("/add", response_model=SymptomDiaryResponse)
def add_diary(data: SymptomDiaryCreate, db: Session = Depends(get_db)):
    entry = SymptomDiary(**data.model_dump())
    db.add(entry)
    db.commit()
    db.refresh(entry)

    log = AgentLog(
        user_id=data.user_id,
        agent_type="SymptomTracker",
        input=f"Symptom: {data.symptom}",
        output=f"Severity: {data.severity}, Mood: {data.mood}",
    )
    db.add(log)
    db.commit()
    return entry


@router.get("/{user_id}", response_model=list[SymptomDiaryResponse])
def get_diary(user_id: UUID, db: Session = Depends(get_db)):
    return db.query(SymptomDiary).filter(SymptomDiary.user_id == user_id).all()


@router.get("/agent/logs/{user_id}", response_model=list[AgentLogResponse])
def get_agent_logs(user_id: UUID, db: Session = Depends(get_db)):
    return db.query(AgentLog).filter(AgentLog.user_id == user_id).all()
