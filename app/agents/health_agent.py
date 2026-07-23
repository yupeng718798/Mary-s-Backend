from sqlalchemy.orm import Session
from app.services.ai_agent import _get_client, ZHIPU_MODEL
from app.tools.medical_tools import (
    get_medical_records,
    get_medications,
    get_symptom_diary,
    get_consultations,
    get_profile,
)


SYSTEM_PROMPT = """你是 Mary 医疗 AI 助手的 Health Summary Agent（健康总览智能体）。

你的职责：
1. 综合汇总用户的所有健康数据
2. 提供整体健康状况评估
3. 识别需要关注的健康风险
4. 给出健康建议和生活方式指导

工作方式：
- 你可以访问用户的病历记录、当前用药、症状日记、问诊记录和基本信息
- 综合分析所有数据，用友好的语言给出总结
- 分点说明，条理清晰
- 指出需要关注的地方和建议的下一步行动
- 始终提醒：AI 分析仅供参考，具体请咨询医生

请用中文回复，语气温馨鼓励。"""


class HealthSummaryAgent:
    name = "Health Summary Agent"
    description = "负责健康总览、综合评估、健康建议"

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

        name = profile.get('full_name', '用户') if profile else '用户'

        context = f"""用户健康总览
姓名: {name}
性别: {profile.get('gender', '未知') if profile else '未知'}

📋 病历记录：{len(records)} 份
"""
        for r in records[:5]:
            context += f"  - {r['title']} ({r['status']})\n"

        context += f"\n💊 当前用药：{len(meds)} 种\n"
        for m in meds[:5]:
            context += f"  - {m['medicine_name']} ({m['dosage']}, {m['frequency']})\n"

        context += f"\n📝 症状日记：{len(diary)} 条\n"
        for d in diary[:3]:
            context += f"  - {d['symptom']} (严重程度: {d['severity']}/10)\n"

        context += f"\n🏥 问诊记录：{len(consultations)} 条\n"

        if self.client is None:
            return (
                f"你好，{name}！👋\n\n"
                f"你的健康总览：\n"
                f"📋 病历记录：{len(records)} 份\n"
                f"💊 当前用药：{len(meds)} 种\n"
                f"📝 症状日记：{len(diary)} 条\n"
                f"🏥 问诊记录：{len(consultations)} 条\n\n"
                f"保持关注健康是好的开始！记得定期复查，按时服药。\n"
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
            return f"Health Summary Agent 出错了：{str(e)}"
