from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.connection import engine, Base
from app.routers import profile, medical, consultation, medication, diary
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Mary Healthcare AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(profile.router)
app.include_router(medical.router)
app.include_router(consultation.router)
app.include_router(medication.router)
app.include_router(diary.router)


@app.on_event("startup")
def on_startup():
    if engine is not None:
        Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "Mary AI Healthcare Backend Running"}


@app.get("/health")
def health():
    if not engine:
        return {"status": "error", "detail": "DATABASE_URL not set"}
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}
