import os
from dotenv import load_dotenv

load_dotenv('d:/ai/Medicine/fastapi-new/medical-rag-backend/.env')

print("ZHIPU_API_KEY:", os.getenv("ZHIPU_API_KEY", "NOT SET"))
print("ZHIPU_BASE_URL:", os.getenv("ZHIPU_BASE_URL", "NOT SET"))
print("ZHIPU_MODEL:", os.getenv("ZHIPU_MODEL", "NOT SET"))