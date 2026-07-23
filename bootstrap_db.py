import os
import psycopg2
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv('d:/ai/Medicine/fastapi-new/medical-rag-backend/.env')
url = os.getenv('DATABASE_URL').strip()
p = urlparse(url)
conn = psycopg2.connect(host=p.hostname, port=p.port, dbname=p.path[1:], user=p.username, password=p.password)
conn.autocommit = True
cur = conn.cursor()

DEMO_ID = '00000000-0000-0000-0000-000000000001'

cur.execute("SELECT id FROM auth.users WHERE id = %s", (DEMO_ID,))
if cur.fetchone() is None:
    print("Creating demo user in auth.users...")
    cur.execute("""
        INSERT INTO auth.users (id, email, aud, role, created_at, updated_at)
        VALUES (%s, 'john@example.com', 'authenticated', 'authenticator', now(), now())
    """, (DEMO_ID,))
    print("Created auth.users row")
else:
    print("auth.users row already exists")

cur.execute("SELECT id FROM profiles WHERE id = %s", (DEMO_ID,))
if cur.fetchone() is None:
    print("Creating demo profile...")
    cur.execute("""
        INSERT INTO profiles (id, full_name, gender, phone, emergency_contact, language)
        VALUES (%s, 'John Smith', 'Male', '+61 400 123 456', '+61 400 123 456', 'English')
    """, (DEMO_ID,))
    print("Created profile")
else:
    print("Profile already exists")

print("\nDone.")
