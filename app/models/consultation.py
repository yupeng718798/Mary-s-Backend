from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.database.connection import Base


class Consultation(Base):
    __tablename__ = "consultations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id"))
    symptoms = Column(Text)
    ai_questions = Column(Text, nullable=True)
    doctor_notes = Column(Text, nullable=True)
    status = Column(String(30), default="preparing")
    created_at = Column(DateTime, server_default=func.now())
