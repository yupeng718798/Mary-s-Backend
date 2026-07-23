from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.database.connection import Base


class MedicalRecord(Base):
    __tablename__ = "medical_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id"))
    title = Column(String(255))
    record_type = Column(String(50))
    file_url = Column(Text, nullable=True)
    upload_date = Column(DateTime, server_default=func.now())
    status = Column(String(30), default="uploaded")


class MedicalAnalysis(Base):
    __tablename__ = "medical_analysis"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    record_id = Column(UUID(as_uuid=True), ForeignKey("medical_records.id"))
    agent_name = Column(String(50), default="Medical Analysis Agent")
    summary = Column(Text)
    risk_level = Column(String(20))
    created_at = Column(DateTime, server_default=func.now())


class GeneratedReport(Base):
    __tablename__ = "generated_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id"))
    report_type = Column(String(50))
    content = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
