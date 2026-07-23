from openai import OpenAI

client = OpenAI(
    api_key="1076d136c7aa44999a2b77a0d65c2f25.QhKswt2m9oN9jrBo",
    base_url="https://open.bigmodel.cn/api/paas/v4",
)

print("Testing GLM-4-flash...")
response = client.chat.completions.create(
    model="glm-4-flash",
    messages=[
        {"role": "system", "content": "你是一个医疗AI助手"},
        {"role": "user", "content": "患者头痛三天，请给出建议"},
    ],
    temperature=0.7,
)
print(response.choices[0].message.content)