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
        "description": "病历分析、检查报告解读、健康风险评估",
        "keywords": ["病历", "报告", "检查", "化验", "分析", "血", "尿", "体检", "结果", "风险"],
    },
    "consultation": {
        "class": ConsultationAgent,
        "name": "Consultation Agent",
        "description": "问诊导航、症状分析、就医流程指引",
        "keywords": ["症状", "看病", "医生", "问诊", "预约", "GP", "专科", "急诊", "疼痛", "不舒服", "头疼", "发烧"],
    },
    "medication": {
        "class": MedicationAgent,
        "name": "Medication Agent",
        "description": "药物管理、用药提醒、药物相互作用",
        "keywords": ["药", "吃药", "服药", "药物", "剂量", "副作用", "提醒", "处方", "药盒"],
    },
    "health": {
        "class": HealthSummaryAgent,
        "name": "Health Summary Agent",
        "description": "健康总览、综合评估、健康建议",
        "keywords": ["健康", "总览", "总结", "概况", "整体", "怎么样", "状况", "状态"],
    },
}


def _keyword_route(message: str) -> str:
    msg = message.lower()
    scores = {}
    for agent_key, agent_info in AGENT_REGISTRY.items():
        score = sum(1 for kw in agent_info["keywords"] if kw in message or kw.lower() in msg)
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

    prompt = f"""根据用户消息，判断应该路由到哪个 AI Agent。

可用的 Agent：
{agent_descriptions}

用户消息：{message}

请只返回 Agent 的 key（medical / consultation / medication / health），不要返回其他内容。
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
    agent_key = _llm_route(message)
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
