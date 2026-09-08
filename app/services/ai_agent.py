import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env file (supports project root or current working directory)
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
                    "content": "You are a medical AI assistant. Analyze the medical text and provide: 1. Brief summary (2-3 sentences) 2. Risk level: low/medium/high 3. Key details to note. Reply in this format: Summary: ...\nRisk: ...\nDetails: ..."
                },
                {"role": "user", "content": f"Medical text: {text}"},
            ],
            temperature=0.7,
        )
        content = response.choices[0].message.content or ""

        summary = "Unable to generate summary"
        risk_level = "unknown"
        details = ""

        for line in content.splitlines():
            if line.lower().startswith("summary:"):
                summary = line.split(":", 1)[1].strip() if ":" in line else line
            elif line.lower().startswith("risk:"):
                risk_level = line.split(":", 1)[1].strip() if ":" in line else "unknown"
            elif line.lower().startswith("details:"):
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
            "summary": f"AI analysis failed: {str(e)}",
            "risk_level": "unknown",
            "details": str(e),
        }


def consultation_analysis(symptoms: str) -> str:
    client = _get_client()
    if client is None:
        return (
            "1. When did your symptoms start?\n"
            "2. How would you describe the severity on a scale of 1-10?\n"
            "3. Are you currently taking any medications?\n"
            "4. Do you have any known allergies or pre-existing conditions?\n"
            "5. Have you experienced similar symptoms before?"
        )

    try:
        response = client.chat.completions.create(
            model=ZHIPU_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a medical AI assistant. Based on the patient's specific symptoms, "
                        "generate 4-5 targeted follow-up questions a doctor should ask to narrow down "
                        "the diagnosis. Each question must be directly relevant to the symptoms described. "
                        "CRITICAL: You MUST reply in English ONLY. Do NOT use any other language. "
                        "Return ONLY numbered questions, one per line, with no extra text."
                    )
                },
                {"role": "user", "content": f"Patient symptoms: {symptoms}"},
            ],
            temperature=0.9,
        )
        content = response.choices[0].message.content or ""
        # Filter out any non-English content
        cleaned = content.strip()
        if not cleaned or any('\u4e00' <= c <= '\u9fff' for c in cleaned):
            # Fallback if AI returned Chinese or empty
            return (
                "1. When did your symptoms start?\n"
                "2. How would you describe the severity on a scale of 1-10?\n"
                "3. Are you currently taking any medications?\n"
                "4. Do you have any known allergies or pre-existing conditions?\n"
                "5. Have you experienced similar symptoms before?"
            )
        return cleaned
    except Exception:
        return (
            "1. When did your symptoms start?\n"
            "2. How would you describe the severity on a scale of 1-10?\n"
            "3. Are you currently taking any medications?\n"
            "4. Do you have any known allergies or pre-existing conditions?\n"
            "5. Have you experienced similar symptoms before?"
        )