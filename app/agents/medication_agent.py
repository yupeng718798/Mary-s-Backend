from sqlalchemy.orm import Session
from app.services.ai_agent import _get_client, ZHIPU_MODEL
from app.tools.medical_tools import (
    get_medications,
    get_symptom_diary,
    get_profile,
)


SYSTEM_PROMPT = """你是 Mary 医疗 AI 助手的 Medication Agent（药物管理智能体）。

你的职责：
1. 管理用户的药物列表和用药提醒
2. 解释药物的作用和注意事项
3. 提醒药物相互作用和常见副作用
4. 回答用药相关问题

工作方式：
- 你可以访问用户的当前用药清单和症状日记
- 提供用药建议：服药时间、饮食禁忌、常见副作用等
- 提醒用户：不要自行停药或换药，有问题咨询医生或药剂师

请用中文回复，语言亲切易懂。始终提醒：AI 建议仅供参考，用药请遵医嘱。"""


class MedicationAgent:
    name = "Medication Agent"
    description = "负责药物管理、用药提醒、药物相互作用查询"

    def __init__(self, db: Session, user_id: str):
        self.db = db
        self.user_id = user_id
        self.client = _get_client()

    def run(self, user_message: str) -> str:
        medications = get_medications(self.db, self.user_id)
        diary = get_symptom_diary(self.db, self.user_id)
        profile = get_profile(self.db, self.user_id)

        context = f"""用户信息：
姓名: {profile.get('full_name', '未知') if profile else '未知'}

当前用药（{len(medications)} 种）：
"""
        for m in medications:
            reminder = f"，提醒时间: {m.get('reminder_time', '未设置')}" if m.get('reminder_time') else ""
            context += f"- {m['medicine_name']} ({m['dosage']}, {m['frequency']}{reminder})\n"

        if diary:
            context += f"\n最近症状日记（最近 {len(diary)} 条）：\n"
            for d in diary[:3]:
                context += f"- {d['symptom']} (严重程度: {d['severity']}/10)\n"

        if self.client is None:
            name = profile.get('full_name', '用户') if profile else '用户'
            return (
                f"你好，{name}！\n\n"
                f"你目前有 {len(medications)} 种药物。\n\n"
                f"我可以帮你：\n"
                f"1. 查看当前用药清单\n"
                f"2. 了解药物服用方法\n"
                f"3. 查询药物注意事项\n"
                f"4. 设置服药提醒\n\n"
                f"（AI 服务未配置，以上为演示回复）"
            )

        try:
            response = self.client.chat.completions.create(
                model=ZHIPU_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"{context}\n\n用户问题：{user_message}"},
                ],
                temperature=0.7,
            )
            return response.choices[0].message.content or "抱歉，我暂时无法回答这个问题。"
        except Exception as e:
            return f"Medication Agent 出错了：{str(e)}"
