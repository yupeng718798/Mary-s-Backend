import os
from dotenv import load_dotenv
from pathlib import Path

# 加载 .env 文件（支持从项目根目录或当前工作目录）
load_dotenv()
load_dotenv(Path(__file__).parent.parent.parent / ".env")

ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY", "")
ZHIPU_BASE_URL = os.getenv("ZHIPU_BASE_URL", "https://open.bigmodel.cn/api/paas/v4")
ZHIPU_MODEL = os.getenv("ZHIPU_MODEL", "glm-4-flash")

_client = None


def _get_client():
    global _client
    if not ZHIPU_API_KEY:
        return None
    if _client is None:
        try:
            from openai import OpenAI
            _client = OpenAI(
                api_key=ZHIPU_API_KEY,
                base_url=ZHIPU_BASE_URL,
            )
        except Exception:
            _client = None
    return _client


def medical_analysis(text: str) -> dict:
    client = _get_client()
    if client is None:
        return {
            "summary": "AI analysis placeholder - set ZHIPU_API_KEY to enable",
            "risk_level": "unknown",
            "details": "Connect ZhiPu API key for real analysis.",
        }

    try:
        response = client.chat.completions.create(
            model=ZHIPU_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "你是一个医疗AI助手。分析医疗文本并提供：1. 简短摘要（2-3句话）2. 风险等级：low/medium/high 3. 需要注意的关键细节。请用以下格式回复：Summary: ...\nRisk: ...\nDetails: ..."
                },
                {"role": "user", "content": f"医疗文本：{text}"},
            ],
            temperature=0.7,
        )
        content = response.choices[0].message.content or ""

        summary = "无法生成摘要"
        risk_level = "unknown"
        details = ""

        for line in content.splitlines():
            if line.lower().startswith("summary:") or line.startswith("摘要") or line.startswith("Summary:"):
                summary = line.split(":", 1)[1].strip() if ":" in line else line
            elif line.lower().startswith("risk:") or line.startswith("风险") or line.startswith("Risk:"):
                risk_level = line.split(":", 1)[1].strip() if ":" in line else "unknown"
            elif line.lower().startswith("details:") or line.startswith("细节") or line.startswith("Details:"):
                details = line.split(":", 1)[1].strip() if ":" in line else ""

        if not details:
            details = content

        return {
            "summary": summary,
            "risk_level": risk_level.lower() if risk_level else "unknown",
            "details": details,
        }
    except Exception as e:
        return {
            "summary": f"AI分析失败: {str(e)}",
            "risk_level": "unknown",
            "details": str(e),
        }


def consultation_analysis(symptoms: str) -> str:
    client = _get_client()
    if client is None:
        return (
            "1. 症状是什么时候开始的？\n"
            "2. 目前是否在服用任何药物？\n"
            "3. 是否有任何已知过敏？\n"
            "4. 请描述疼痛等级（1-10）"
        )

    try:
        response = client.chat.completions.create(
            model=ZHIPU_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "你是一个医疗AI助手。根据患者的症状，生成4-5个医生应该询问的具体问题来缩小诊断范围。只需返回编号的问题，每行一个。"
                },
                {"role": "user", "content": f"患者症状：{symptoms}"},
            ],
            temperature=0.7,
        )
        content = response.choices[0].message.content or ""
        return content.strip() or (
            "1. 症状是什么时候开始的？\n"
            "2. 目前是否在服用任何药物？\n"
            "3. 是否有任何已知过敏？\n"
            "4. 请描述疼痛等级（1-10）"
        )
    except Exception:
        return (
            "1. 症状是什么时候开始的？\n"
            "2. 目前是否在服用任何药物？\n"
            "3. 是否有任何已知过敏？\n"
            "4. 请描述疼痛等级（1-10）"
        )