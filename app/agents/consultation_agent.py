from sqlalchemy.orm import Session
from app.services.ai_agent import _get_client, ZHIPU_MODEL
from app.tools.medical_tools import (
    get_consultations,
    get_medical_records,
    get_profile,
)


SYSTEM_PROMPT = """你是 Mary 医疗 AI 助手的 Consultation Agent（问诊导航智能体）。

你的职责：
1. 帮用户梳理症状，判断严重程度
2. 生成看医生时应该问的问题清单
3. 提供就诊流程指引（GP → Specialist）
4. 提醒看诊前需要准备什么

工作方式：
- 你可以访问用户的问诊历史、病历记录和基本信息
- 当用户描述症状时，先了解症状持续时间、严重程度等
- 生成 4-5 个建议问医生的具体问题
- 给出就诊建议：家庭医生 / 专科 / 急诊
- 提醒准备材料：检查报告、药物清单、既往病史

请用中文回复，语气亲切自然。始终提醒：AI 建议仅供参考，不能替代医生诊断。"""


class ConsultationAgent:
    name = "Consultation Agent"
    description = "负责问诊导航、症状分析、就医流程指引"

    def __init__(self, db: Session, user_id: str):
        self.db = db
        self.user_id = user_id
        self.client = _get_client()

    def run(self, user_message: str) -> str:
        consultations = get_consultations(self.db, self.user_id)
        records = get_medical_records(self.db, self.user_id)
        profile = get_profile(self.db, self.user_id)

        context = f"""用户信息：
姓名: {profile.get('full_name', '未知') if profile else '未知'}

既往病历（最近 {len(records)} 条）：
"""
        for r in records:
            context += f"- {r['title']} ({r['record_type']})\n"

        if consultations:
            context += f"\n问诊历史（最近 {len(consultations)} 条）：\n"
            for c in consultations[:3]:
                context += f"- 症状: {c['symptoms'][:50]}...\n  状态: {c['status']}\n"

        if self.client is None:
            return (
                "我来帮你整理一下问诊思路！\n\n"
                "看医生前建议准备好这些问题：\n"
                "1. 我的症状可能是什么原因引起的？\n"
                "2. 需要做什么检查吗？\n"
                "3. 这种情况需要复诊吗？\n"
                "4. 日常生活有什么需要注意的？\n\n"
                "请告诉我你的具体症状，我可以帮你更有针对性地准备。"
            )

        try:
            response = self.client.chat.completions.create(
                model=ZHIPU_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"{context}\n\n用户描述的症状/问题：{user_message}"},
                ],
                temperature=0.7,
            )
            return response.choices[0].message.content or "抱歉，我暂时无法回答这个问题。"
        except Exception as e:
            return f"Consultation Agent 出错了：{str(e)}"
