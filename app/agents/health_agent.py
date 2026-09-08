from sqlalchemy.orm import Session
from app.services.ai_agent import _get_client, ZHIPU_MODEL
from app.tools.medical_tools import (
    get_medical_records,
    get_medications,
    get_symptom_diary,
    get_consultations,
    get_profile,
)


SYSTEM_PROMPT = """You are the Health Summary Agent of Mary Healthcare AI.

Your responsibilities:
1. Summarize all of the user's health data comprehensively
2. Provide an overall health assessment
3. Identify health risks that need attention
4. Give health recommendations and lifestyle guidance

Workflow:
- You have access to the user's medical records, current medications, symptom diary, consultation history, and basic profile
- Analyze all data and give a friendly summary
- Use bullet points for clarity
- Highlight areas of concern and suggested next steps
- Always remind: AI analysis is for reference only — consult a doctor for specifics

Reply in English, in a warm and encouraging tone."""

class HealthSummaryAgent:
    name = "Health Summary Agent"
    description = "Health overview, comprehensive assessment, wellness recommendations"

    def __init__(self, db: Session, user_id: str):
        self.db = db
        self.user_id = user_id
        self.client = _get_client()

    def run(self, user_message: str) -> str:
        records = get_medical_records(self.db, self.user_id)
        meds = get_medications(self.db, self.user_id)
        diary = get_symptom_diary(self.db, self.user_id)
        consultations = get_consultations(self.db, self.user_id)
        profile = get_profile(self.db, self.user_id)

        name = profile.get('full_name', 'User') if profile else 'User'

        context = f"""User Health Overview
Name: {name}
Gender: {profile.get('gender', 'Unknown') if profile else 'Unknown'}

Medical Records: {len(records)}
"""
        for r in records[:5]:
            context += f"  - {r['title']} ({r['status']})\n"

        context += f"\nCurrent Medications: {len(meds)}\n"
        for m in meds[:5]:
            context += f"  - {m['medicine_name']} ({m['dosage']}, {m['frequency']})\n"

        context += f"\nSymptom Diary: {len(diary)} entries\n"
        for d in diary[:3]:
            context += f"  - {d['symptom']} (Severity: {d['severity']}/10)\n"

        context += f"\nConsultation Records: {len(consultations)}\n"

        if self.client is None:
            return (
                f"Hello, {name}!\n\n"
                f"Your Health Overview:\n"
                f"Medical Records: {len(records)}\n"
                f"Current Medications: {len(meds)}\n"
                f"Symptom Diary: {len(diary)} entries\n"
                f"Consultation Records: {len(consultations)}\n\n"
                f"Staying on top of your health is a great start! Remember to schedule regular check-ups and take your medications on time.\n"
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
            return f"Health Summary Agent error: {str(e)}"

    def run_stream(self, user_message: str):
        records = get_medical_records(self.db, self.user_id)
        meds = get_medications(self.db, self.user_id)
        diary = get_symptom_diary(self.db, self.user_id)
        consultations = get_consultations(self.db, self.user_id)
        profile = get_profile(self.db, self.user_id)

        name = profile.get('full_name', 'User') if profile else 'User'

        context = f"""User Health Overview
Name: {name}
Gender: {profile.get('gender', 'Unknown') if profile else 'Unknown'}

Medical Records: {len(records)}
"""
        for r in records[:5]:
            context += f"  - {r['title']} ({r['status']})\n"

        context += f"\nCurrent Medications: {len(meds)}\n"
        for m in meds[:5]:
            context += f"  - {m['medicine_name']} ({m['dosage']}, {m['frequency']})\n"

        context += f"\nSymptom Diary: {len(diary)} entries\n"
        for d in diary[:3]:
            context += f"  - {d['symptom']} (Severity: {d['severity']}/10)\n"

        context += f"\nConsultation Records: {len(consultations)}\n"

        if self.client is None:
            yield (
                f"Hello, {name}!\n\n"
                f"Your Health Overview:\n"
                f"Medical Records: {len(records)}\n"
                f"Current Medications: {len(meds)}\n"
                f"Symptom Diary: {len(diary)} entries\n"
                f"Consultation Records: {len(consultations)}\n\n"
                f"Staying on top of your health is a great start! Remember to schedule regular check-ups and take your medications on time.\n"
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
            yield f"Health Summary Agent error: {str(e)}"