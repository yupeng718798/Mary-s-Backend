from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = os.getenv("DATABASE_URL")
engine = None
if DATABASE_URL:
    try:
        engine = create_engine(DATABASE_URL)
    except Exception as e:
        print(f"Failed to create engine: {e}")


@app.get("/")
def root():
    return {"message": "backend running"}


@app.get("/test")
def test():
    return "收到"


@app.get("/health")
def health():
    if not engine:
        return {"status": "error", "detail": "DATABASE_URL not set"}
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


@app.get("/users")
def get_users():
    if not engine:
        raise HTTPException(status_code=500, detail="DATABASE_URL not configured")
    try:
        with engine.connect() as conn:
            result = conn.execute(text("select * from users"))
            users = []
            for row in result:
                users.append({
                    "id": row.id,
                    "name": row.name,
                    "email": row.email
                })
            return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))