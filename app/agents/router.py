from sqlalchemy.orm import Session
from app.agents.medical_agent import MedicalAgent
from app.agents.consultation_agent import ConsultationAgent
from app.agents.medication_agent import MedicationAgent
from app.agents.health_agent import HealthSummaryAgent
from app.services.ai_agent import _get_client, ZHIPU_MODEL
from app.models.medication import AgentLog


AGENT_REGISTRY = {
    "medical": {
        "class": MedicalAgent,
        "name": "Medical Analysis Agent",
        "description": "Medical record analysis, lab report interpretation, health risk assessment",
        "keywords": ["record", "report", "test", "lab", "analysis", "blood", "urine", "exam", "result", "risk"],
    },
    "consultation": {
        "class": ConsultationAgent,
        "name": "Consultation Agent",
        "description": "Consultation navigation, symptom analysis, healthcare visit guidance",
        "keywords": ["symptom", "doctor", "consult", "appointment", "GP", "specialist", "emergency", "pain", "sick", "headache", "fever"],
    },
    "medication": {
        "class": MedicationAgent,
        "name": "Medication Agent",
        "description": "Medication management, dosage reminders, drug interaction lookup",
        "keywords": ["medication", "drug", "pill", "dose", "dosage", "side effect", "reminder", "prescription", "medicine"],
    },
    "health": {
        "class": HealthSummaryAgent,
        "name": "Health Summary Agent",
        "description": "Health overview, comprehensive assessment, wellness recommendations",
        "keywords": ["health", "summary", "overview", "overall", "status", "condition", "wellness"],
    },
}


def _keyword_route(message: str) -> str:
    msg = message.lower()
    scores = {}
    for agent_key, agent_info in AGENT_REGISTRY.items():
        score = sum(1 for kw in agent_info["keywords"] if kw.lower() in msg)
        scores[agent_key] = score
    best_agent = max(scores, key=scores.get)
    if scores[best_agent] > 0:
        return best_agent
    return "health"


def _llm_route(message: str) -> str:
    client = _get_client()
    if client is None:
        return _keyword_route(message)

    agent_descriptions = "\n".join(
        [f"- {key}: {info['description']}" for key, info in AGENT_REGISTRY.items()]
    )

    prompt = f"""Based on the user message, determine which AI Agent to route to.

Available Agents:
{agent_descriptions}

User Message: {message}

Return only the Agent key (medical / consultation / medication / health), nothing else.
"""

    try:
        response = client.chat.completions.create(
            model=ZHIPU_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
        )
        result = response.choices[0].message.content or ""
        result = result.strip().lower()
        for key in AGENT_REGISTRY:
            if key in result:
                return key
        return _keyword_route(message)
    except Exception:
        return _keyword_route(message)


def route_and_run(db: Session, user_id: str, message: str) -> dict:
    # Use keyword routing to avoid extra LLM call (saves 10-20 seconds)
    agent_key = _keyword_route(message)
    agent_info = AGENT_REGISTRY.get(agent_key, AGENT_REGISTRY["health"])
    agent_class = agent_info["class"]
    agent = agent_class(db, user_id)
    response = agent.run(message)

    try:
        log = AgentLog(
            user_id=user_id,
            agent_type=agent_info["name"],
            input=message,
            output=response,
            model=ZHIPU_MODEL,
        )
        db.add(log)
        db.commit()
    except Exception:
        db.rollback()

    return {
        "agent": agent_info["name"],
        "agent_key": agent_key,
        "response": response,
    }


def route_and_run_stream(db: Session, user_id: str, message: str):
    """Streaming route: keyword routing + Agent streaming output"""
    agent_key = _keyword_route(message)
    agent_info = AGENT_REGISTRY.get(agent_key, AGENT_REGISTRY["health"])
    agent_class = agent_info["class"]
    agent = agent_class(db, user_id)

    # Send agent metadata first
    yield {"type": "meta", "agent": agent_info["name"], "agent_key": agent_key}

    # Stream agent response
    full_response = ""
    for chunk in agent.run_stream(message):
        full_response += chunk
        yield {"type": "content", "content": chunk}

    # Save log
    try:
        log = AgentLog(
            user_id=user_id,
            agent_type=agent_info["name"],
            input=message,
            output=full_response,
            model=ZHIPU_MODEL,
        )
        db.add(log)
        db.commit()
    except Exception:
        db.rollback()