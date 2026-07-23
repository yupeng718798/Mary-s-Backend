from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class ConsultationCreate(BaseModel):
    user_id: UUID
    symptoms: str


class ConsultationUpdate(BaseModel):
    doctor_notes: Optional[str] = None
    status: Optional[str] = None


class ConsultationResponse(BaseModel):
    id: UUID
    user_id: UUID
    symptoms: str
    ai_questions: Optional[str] = None
    doctor_notes: Optional[str] = None
    status: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
