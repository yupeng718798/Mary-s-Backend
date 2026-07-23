from pydantic import BaseModel
from typing import Optional
from datetime import time, datetime
from uuid import UUID


class MedicationCreate(BaseModel):
    user_id: UUID
    medicine_name: str
    dosage: str
    frequency: str
    reminder_time: Optional[time] = None
    note: Optional[str] = None


class MedicationResponse(BaseModel):
    id: UUID
    user_id: UUID
    medicine_name: str
    dosage: str
    frequency: str
    reminder_time: Optional[time] = None
    note: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SymptomDiaryCreate(BaseModel):
    user_id: UUID
    symptom: str
    mood: Optional[str] = None
    severity: int
    notes: Optional[str] = None


class SymptomDiaryResponse(BaseModel):
    id: UUID
    user_id: UUID
    symptom: str
    mood: Optional[str] = None
    severity: int
    notes: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AgentLogResponse(BaseModel):
    id: UUID
    user_id: UUID
    agent_type: str
    input: Optional[str] = None
    output: Optional[str] = None
    model: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
