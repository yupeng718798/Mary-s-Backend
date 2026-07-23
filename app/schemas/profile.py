from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
from uuid import UUID


class ProfileBase(BaseModel):
    full_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    emergency_contact: Optional[str] = None
    language: Optional[str] = "English"


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    emergency_contact: Optional[str] = None
    language: Optional[str] = None


class ProfileResponse(ProfileBase):
    id: UUID
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
