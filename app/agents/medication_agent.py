from sqlalchemy.orm import Session
from app.services.ai_agent import _get_client, ZHIPU_MODEL
from app.tools.medical_tools import (
    get_medications,
    get_symptom_diary,
    get_profile,
)


SYSTEM_PROMPT = """You are the Medication Agent of Mary Healthcare AI.

Your responsibilities:
1. Manage the user's medication list and reminders
2. Explain drug effects and precautions
3. Flag potential drug interactions and common side effects
4. Answer medication-related questions

Workflow:
- You have access to the user's current medication list and symptom diary
- Provide medication advice: timing, dietary restrictions, common side effects
- Remind users: never stop or change medications without consulting a doctor or pharmacist

Reply in English, in a friendly and easy-to-understand tone. Always remind: AI advice is for reference only — follow your doctor's prescription."""

class MedicationAgent:
    name = "Medication Agent"
    description = "Medication management, dosage reminders, drug interaction lookup"

    def __init__(self, db: Session, user_id: str):
        self.db = db
        self.user_id = user_id
        self.client = _get_client()

    def run(self, user_message: str) -> str:
        medications = get_medications(self.db, self.user_id)
        diary = get_symptom_diary(self.db, self.user_id)
        profile = get_profile(self.db, self.user_id)

        context = f"""User Info:
Name: {profile.get('full_name', 'Unknown') if profile else 'Unknown'}

Current Medications ({len(medications)}):
"""
        for m in medications:
            reminder = f", Reminder: {m.get('reminder_time', 'Not set')}" if m.get('reminder_time') else ""
            context += f"- {m['medicine_name']} ({m['dosage']}, {m['frequency']}{reminder})\n"

        if diary:
            context += f"\nRecent Symptom Diary (recent {len(diary)} entries):\n"
            for d in diary[:3]:
                context += f"- {d['symptom']} (Severity: {d['severity']}/10)\n"

        if self.client is None:
            name = profile.get('full_name', 'User') if profile else 'User'
            return (
                f"Hello, {name}!\n\n"
                f"You currently have {len(medications)} medication(s).\n\n"
                f"I can help you with:\n"
                f"1. Viewing your current medication list\n"
                f"2. Understanding how to take your medications\n"
                f"3. Checking drug precautions\n"
                f"4. Setting up medication reminders\n\n"
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
            return f"Medication Agent error: {str(e)}"

    def run_stream(self, user_message: str):
        medications = get_medications(self.db, self.user_id)
        diary = get_symptom_diary(self.db, self.user_id)
        profile = get_profile(self.db, self.user_id)

        context = f"""User Info:
Name: {profile.get('full_name', 'Unknown') if profile else 'Unknown'}

Current Medications ({len(medications)}):
"""
        for m in medications:
            reminder = f", Reminder: {m.get('reminder_time', 'Not set')}" if m.get('reminder_time') else ""
            context += f"- {m['medicine_name']} ({m['dosage']}, {m['frequency']}{reminder})\n"

        if diary:
            context += f"\nRecent Symptom Diary (recent {len(diary)} entries):\n"
            for d in diary[:3]:
                context += f"- {d['symptom']} (Severity: {d['severity']}/10)\n"

        if self.client is None:
            name = profile.get('full_name', 'User') if profile else 'User'
            yield (
                f"Hello, {name}!\n\n"
                f"You currently have {len(medications)} medication(s).\n\n"
                f"I can help you with:\n"
                f"1. Viewing your current medication list\n"
                f"2. Understanding how to take your medications\n"
                f"3. Checking drug precautions\n"
                f"4. Setting up medication reminders\n\n"
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
            yield f"Medication Agent error: {str(e)}"