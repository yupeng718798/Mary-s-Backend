from sqlalchemy.orm import Session
from app.services.ai_agent import _get_client, ZHIPU_MODEL
from app.tools.medical_tools import (
    get_medical_records,
    get_medical_analysis,
    get_profile,
)


SYSTEM_PROMPT = """You are the Medical Analysis Agent of Mary Healthcare AI.

Your responsibilities:
1. Help users query and analyze medical records
2. Explain lab reports and test results in plain language
3. Provide easy-to-understand medical explanations
4. Flag risk indicators that need attention

Workflow:
- You have access to the user's medical records and basic profile
- Summarize findings in plain, accessible language
- Risk levels: Low / Medium / High
- Always remind: AI analysis is for reference only and does not replace a doctor's diagnosis

Reply in English, in a warm and professional tone."""

class MedicalAgent:
    name = "Medical Analysis Agent"
    description = "Medical record analysis, lab report interpretation, health risk assessment"

    def __init__(self, db: Session, user_id: str):
        self.db = db
        self.user_id = user_id
        self.client = _get_client()

    def run(self, user_message: str) -> str:
        records = get_medical_records(self.db, self.user_id)
        profile = get_profile(self.db, self.user_id)

        analyses = []
        for r in records[:3]:
            analysis = get_medical_analysis(self.db, r["id"])
            if analysis:
                analyses.append(analysis)

        context = f"""User Info:
Name: {profile.get('full_name', 'Unknown') if profile else 'Unknown'}
Gender: {profile.get('gender', 'Unknown') if profile else 'Unknown'}

Medical Records (recent {len(records)}):
"""
        for r in records:
            context += f"- {r['title']} ({r['record_type']}, Status: {r['status']})\n"

        if analyses:
            context += "\nAnalyzed Reports:\n"
            for a in analyses:
                context += f"- Summary: {a.get('summary', 'N/A')}\n  Risk Level: {a.get('risk_level', 'Unknown')}\n"

        if self.client is None:
            name = profile.get('full_name', 'User') if profile else 'User'
            return (
                f"Hello, {name}!\n\n"
                f"You currently have {len(records)} medical record(s).\n\n"
                f"I can help you with:\n"
                f"1. Viewing your medical record list\n"
                f"2. Analyzing lab reports\n"
                f"3. Interpreting test results\n\n"
                f"(AI service not configured — demo response)"
            )

        try:
            response = self.client.chat.completions.create(
                model=ZHIPU_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"{context}\n\nUser Question: {user_message}"},
                ],
                temperature=0.7,
            )
            return response.choices[0].message.content or "Sorry, I'm unable to answer this right now."
        except Exception as e:
            return f"Medical Agent error: {str(e)}"

    def run_stream(self, user_message: str):
        """Streaming: yields LLM tokens as they are generated"""
        records = get_medical_records(self.db, self.user_id)
        profile = get_profile(self.db, self.user_id)

        analyses = []
        for r in records[:3]:
            analysis = get_medical_analysis(self.db, r["id"])
            if analysis:
                analyses.append(analysis)

        context = f"""User Info:
Name: {profile.get('full_name', 'Unknown') if profile else 'Unknown'}
Gender: {profile.get('gender', 'Unknown') if profile else 'Unknown'}

Medical Records (recent {len(records)}):
"""
        for r in records:
            context += f"- {r['title']} ({r['record_type']}, Status: {r['status']})\n"

        if analyses:
            context += "\nAnalyzed Reports:\n"
            for a in analyses:
                context += f"- Summary: {a.get('summary', 'N/A')}\n  Risk Level: {a.get('risk_level', 'Unknown')}\n"

        if self.client is None:
            name = profile.get('full_name', 'User') if profile else 'User'
            yield (
                f"Hello, {name}!\n\n"
                f"You currently have {len(records)} medical record(s).\n\n"
                f"I can help you with:\n"
                f"1. Viewing your medical record list\n"
                f"2. Analyzing lab reports\n"
                f"3. Interpreting test results\n\n"
                f"(AI service not configured — demo response)"
            )
            return

        try:
            response = self.client.chat.completions.create(
                model=ZHIPU_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"{context}\n\nUser Question: {user_message}"},
                ],
                temperature=0.7,
                stream=True,
            )
            for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            yield f"Medical Agent error: {str(e)}"