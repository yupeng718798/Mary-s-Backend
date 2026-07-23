from sqlalchemy.orm import Session
from app.services.ai_agent import _get_client, ZHIPU_MODEL
from app.tools.medical_tools import (
    get_medical_records,
    get_medical_analysis,
    get_profile,
)


SYSTEM_PROMPT = """你是 Mary 医疗 AI 助手的 Medical Analysis Agent（病历分析智能体）。

你的职责：
1. 帮用户查询和分析医疗记录
2. 解释检查报告和化验结果
3. 提供通俗易懂的医学解释
4. 提醒需要关注的风险指标

工作方式：
- 你可以访问用户的病历记录和基本信息
- 用通俗易懂的语言总结，避免过于专业的术语
- 风险等级用中文标注：低风险 / 中风险 / 高风险
- 始终提醒：AI 分析仅供参考，不能替代医生诊断

请用中文回复，语气亲切专业。"""


class MedicalAgent:
    name = "Medical Analysis Agent"
    description = "负责病历分析、检查报告解读、健康风险评估"

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

        context = f"""用户信息：
姓名: {profile.get('full_name', '未知') if profile else '未知'}
性别: {profile.get('gender', '未知') if profile else '未知'}

病历记录（最近 {len(records)} 条）：
"""
        for r in records:
            context += f"- {r['title']} ({r['record_type']}, 状态: {r['status']})\n"

        if analyses:
            context += "\n已分析的报告：\n"
            for a in analyses:
                context += f"- 摘要: {a.get('summary', '无')}\n  风险等级: {a.get('risk_level', '未知')}\n"

        if self.client is None:
            name = profile.get('full_name', '用户') if profile else '用户'
            return (
                f"你好，{name}！\n\n"
                f"你目前有 {len(records)} 份病历记录。\n\n"
                f"我可以帮你：\n"
                f"1. 查看病历列表\n"
                f"2. 分析检查报告\n"
                f"3. 解读化验指标\n\n"
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
            return f"Medical Agent 出错了：{str(e)}"
