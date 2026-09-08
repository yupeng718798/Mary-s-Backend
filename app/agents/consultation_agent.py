from sqlalchemy.orm import Session
from app.services.ai_agent import _get_client, ZHIPU_MODEL
from app.tools.medical_tools import (
    get_consultations,
    get_medical_records,
    get_profile,
)


SYSTEM_PROMPT = """You are the Consultation Agent of Mary Healthcare AI.

Your responsibilities:
1. Help users organize symptoms and assess severity
2. Generate a list of questions to ask the doctor
3. Provide visit navigation guidance (GP -> Specialist)
4. Remind users what to prepare before a doctor's visit

Workflow:
- You have access to the user's consultation history, medical records, and basic profile
- When users describe symptoms, ask about duration, severity, etc.
- Generate 4-5 specific questions to ask the doctor
- Give visit advice: GP / Specialist / Emergency
- Remind them to prepare: test reports, medication list, medical history

Reply in English, in a warm and natural tone. Always remind: AI advice is for reference only and does not replace a doctor's diagnosis."""

class ConsultationAgent:
    name = "Consultation Agent"
    description = "Consultation navigation, symptom analysis, healthcare visit guidance"

    def __init__(self, db: Session, user_id: str):
        self.db = db
        self.user_id = user_id
        self.client = _get_client()

    def run(self, user_message: str) -> str:
        consultations = get_consultations(self.db, self.user_id)
        records = get_medical_records(self.db, self.user_id)
        profile = get_profile(self.db, self.user_id)

        context = f"""User Info:
Name: {profile.get('full_name', 'Unknown') if profile else 'Unknown'}

Medical History (recent {len(records)} records):
"""
        for r in records:
            context += f"- {r['title']} ({r['record_type']})\n"

        if consultations:
            context += f"\nConsultation History (recent {len(consultations)}):\n"
            for c in consultations[:3]:
                context += f"- Symptoms: {c['symptoms'][:50]}...\n  Status: {c['status']}\n"

        if self.client is None:
            return (
                "Let me help you organize your consultation approach!\n\n"
                "Here are questions to prepare before seeing a doctor:\n"
                "1. What could be causing my symptoms?\n"
                "2. What tests do I need?\n"
                "3. Will I need a follow-up appointment?\n"
                "4. What lifestyle changes should I consider?\n\n"
                "Tell me your specific symptoms and I can help you prepare better."
            )

        try:
            response = self.client.chat.completions.create(
                model=ZHIPU_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"{context}\n\nUser's symptoms / question: {user_message}"},
                ],
                temperature=0.7,
            )
            return response.choices[0].message.content or "Sorry, I'm unable to answer this right now."
        except Exception as e:
            return f"Consultation Agent error: {str(e)}"

    def run_stream(self, user_message: str):
        consultations = get_consultations(self.db, self.user_id)
        records = get_medical_records(self.db, self.user_id)
        profile = get_profile(self.db, self.user_id)

        context = f"""User Info:
Name: {profile.get('full_name', 'Unknown') if profile else 'Unknown'}

Medical History (recent {len(records)} records):
"""
        for r in records:
            context += f"- {r['title']} ({r['record_type']})\n"

        if consultations:
            context += f"\nConsultation History (recent {len(consultations)}):\n"
            for c in consultations[:3]:
                context += f"- Symptoms: {c['symptoms'][:50]}...\n  Status: {c['status']}\n"

        if self.client is None:
            yield (
                "Let me help you organize your consultation approach!\n\n"
                "Here are questions to prepare before seeing a doctor:\n"
                "1. What could be causing my symptoms?\n"
                "2. What tests do I need?\n"
                "3. Will I need a follow-up appointment?\n"
                "4. What lifestyle changes should I consider?\n\n"
                "Tell me your specific symptoms and I can help you prepare better."
            )
            return

        try:
            response = self.client.chat.completions.create(
                model=ZHIPU_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"{context}\n\nUser's symptoms / question: {user_message}"},
                ],
                temperature=0.7,
                stream=True,
            )
            for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            yield f"Consultation Agent error: {str(e)}"