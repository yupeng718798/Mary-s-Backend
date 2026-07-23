import os
import psycopg2
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv('d:/ai/Medicine/fastapi-new/medical-rag-backend/.env')
url = os.getenv('DATABASE_URL').strip()
p = urlparse(url)
conn = psycopg2.connect(host=p.hostname, port=p.port, dbname=p.path[1:], user=p.username, password=p.password)
cur = conn.cursor()

print("=== profiles columns ===")
cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name='profiles'")
for r in cur.fetchall():
    print(r)

print("\n=== profiles constraints ===")
cur.execute("SELECT conname, contype, pg_get_constraintdef(oid) FROM pg_constraint WHERE conrelid = 'profiles'::regclass")
for r in cur.fetchall():
    print(r)

print("\n=== users columns ===")
cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name='users'")
for r in cur.fetchall():
    print(r)

print("\n=== users rows ===")
cur.execute("SELECT * FROM users LIMIT 5")
for r in cur.fetchall():
    print(r)

print("\n=== profiles rows ===")
cur.execute("SELECT * FROM profiles LIMIT 5")
for r in cur.fetchall():
    print(r)
