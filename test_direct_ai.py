import os, sys
sys.path.insert(0, 'd:/ai/Medicine/fastapi-new/medical-rag-backend')
from app.services.ai_agent import medical_analysis, consultation_analysis

print("Testing consultation_analysis...")
result = consultation_analysis("headache for 3 days with dizziness")
print("Consultation result:")
print(result)

print("\nTesting medical_analysis...")
result = medical_analysis("Patient has high blood pressure and cholesterol")
print("Medical result:")
print(result)
