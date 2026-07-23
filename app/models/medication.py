from sqlalchemy import Column, String, Text, Integer, Time, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.database.connection import Base


class Medication(Base):
    __tablename__ = "medications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id"))
    medicine_name = Column(String(100))
    dosage = Column(String(50))
    frequency = Column(String(50))
    reminder_time = Column(Time, nullable=True)
    note = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class SymptomDiary(Base):
    __tablename__ = "symptom_diary"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id"))
    symptom = Column(Text)
    mood = Column(String(20), nullable=True)
    severity = Column(Integer)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class AgentLog(Base):
    __tablename__ = "agent_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id"))
    agent_type = Column(String(50))
    input = Column(Text, nullable=True)
    output = Column(Text, nullable=True)
    model = Column(String(50), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
