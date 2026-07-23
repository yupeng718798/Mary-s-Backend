from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
import uuid
from app.database.connection import get_db
from app.models.profile import Profile
from app.schemas.profile import ProfileCreate, ProfileUpdate, ProfileResponse

router = APIRouter(prefix="/api/profile", tags=["Profile"])


DEMO_USER_ID = UUID("00000000-0000-0000-0000-000000000001")


@router.post("/bootstrap", response_model=ProfileResponse)
def bootstrap_profile(db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.id == DEMO_USER_ID).first()
    if profile:
        return profile
    profile = Profile(
        id=DEMO_USER_ID,
        full_name="John Smith",
        gender="Male",
        phone="+61 400 123 456",
        emergency_contact="+61 400 123 456",
        language="English",
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.get("/{user_id}", response_model=ProfileResponse)
def get_profile(user_id: UUID, db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.post("/", response_model=ProfileResponse)
def create_profile(data: ProfileCreate, db: Session = Depends(get_db)):
    payload = data.model_dump()
    payload["id"] = uuid.uuid4()
    profile = Profile(**payload)
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.put("/{user_id}", response_model=ProfileResponse)
def update_profile(user_id: UUID, data: ProfileUpdate, db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(profile, key, value)
    db.commit()
    db.refresh(profile)
    return profile
