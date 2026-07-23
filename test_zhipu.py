import os
import sys
sys.path.insert(0, 'd:/ai/Medicine/fastapi-new/medical-rag-backend')
from app.services.ai_agent import medical_analysis, consultation_analysis

print("测试智谱 GLM API...")
print("\n=== 测试 consultation_analysis ===")
result = consultation_analysis("头痛三天，伴有头晕")
print(result)

print("\n=== 测试 medical_analysis ===")
result = medical_analysis("患者血压偏高，胆固醇偏高")
print(result)