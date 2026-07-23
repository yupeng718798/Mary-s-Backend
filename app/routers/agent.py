from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from uuid import UUID
from app.database.connection import get_db
from app.agents.router import route_and_run, AGENT_REGISTRY
from app.models.medication import AgentLog


router = APIRouter(prefix="/api/agent", tags=["AI Agent"])


class ChatRequest(BaseModel):
    user_id: str
    message: str


class ChatResponse(BaseModel):
    agent: str
    agent_key: str
    response: str


@router.post("/chat", response_model=ChatResponse)
def agent_chat(req: ChatRequest, db: Session = Depends(get_db)):
    try:
        result = route_and_run(db, req.user_id, req.message)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
def list_agents():
    return [
        {"key": key, "name": info["name"], "description": info["description"]}
        for key, info in AGENT_REGISTRY.items()
    ]


@router.get("/logs/{user_id}")
def get_agent_logs(user_id: UUID, db: Session = Depends(get_db), limit: int = 20):
    logs = (
        db.query(AgentLog)
        .filter(AgentLog.user_id == user_id)
        .order_by(AgentLog.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": str(log.id),
            "agent_type": log.agent_type,
            "input": log.input,
            "output": log.output,
            "model": log.model,
            "created_at": log.created_at.isoformat() if log.created_at else None,
        }
        for log in logs
    ]
