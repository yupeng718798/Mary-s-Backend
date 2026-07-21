from fastapi import FastAPI
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
engine = create_engine(DATABASE_URL)


@app.get("/")
def root():
    return {"message": "backend running"}


@app.get("/test")
def test():
    return "收到"


@app.get("/users")
def get_users():
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