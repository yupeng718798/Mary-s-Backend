from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class MedicalRecordCreate(BaseModel):
    user_id: UUID
    title: str
    record_type: str


class MedicalRecordResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    record_type: str
    file_url: Optional[str] = None
    status: str
    upload_date: Optional[datetime] = None

    class Config:
        from_attributes = True


class MedicalAnalysisResponse(BaseModel):
    id: UUID
    record_id: UUID
    agent_name: Optional[str] = None
    summary: Optional[str] = None
    risk_level: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ReportCreate(BaseModel):
    record_id: UUID
    user_id: UUID
    report_type: Optional[str] = None


class ReportResponse(BaseModel):
    id: UUID
    user_id: UUID
    report_type: Optional[str] = None
    content: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
