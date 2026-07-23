import urllib.request, json

# Test consultation - quick
req = urllib.request.Request(
    'http://127.0.0.1:8001/api/consultation/create',
    method='POST',
    data=json.dumps({"user_id": "00000000-0000-0000-0000-000000000001", "symptoms": "headache for 3 days"}).encode(),
    headers={'Content-Type': 'application/json'},
)
try:
    resp = urllib.request.urlopen(req, timeout=60)
    data = json.loads(resp.read().decode())
    print("CONSULTATION:", json.dumps(data, indent=2))
except Exception as e:
    print("ERR:", e)
