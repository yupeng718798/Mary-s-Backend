import urllib.request, json

record_id = 'bf49f7f0-909f-47f4-9665-4102555984cf'

# Analyze
req = urllib.request.Request(
    f'http://127.0.0.1:8001/api/medical/analyze/{record_id}',
    method='POST',
)
resp = urllib.request.urlopen(req)
data = json.loads(resp.read().decode())
print("ANALYZE result:")
print(json.dumps(data, indent=2))

# Consultation
req = urllib.request.Request(
    'http://127.0.0.1:8001/api/consultation/create',
    method='POST',
    data=json.dumps({"user_id": "00000000-0000-0000-0000-000000000001", "symptoms": "headache for 3 days with dizziness"}).encode(),
    headers={'Content-Type': 'application/json'},
)
resp = urllib.request.urlopen(req)
data = json.loads(resp.read().decode())
print("\nCONSULTATION result:")
print(json.dumps(data, indent=2))

# Medication add
req = urllib.request.Request(
    'http://127.0.0.1:8001/api/medication/add',
    method='POST',
    data=json.dumps({
        "user_id": "00000000-0000-0000-0000-000000000001",
        "medicine_name": "Panadol",
        "dosage": "500mg",
        "frequency": "Every 8 hours",
        "reminder_time": "20:00:00",
    }).encode(),
    headers={'Content-Type': 'application/json'},
)
resp = urllib.request.urlopen(req)
data = json.loads(resp.read().decode())
print("\nMEDICATION add:")
print(json.dumps(data, indent=2))

# Diary
req = urllib.request.Request(
    'http://127.0.0.1:8001/api/diary/add',
    method='POST',
    data=json.dumps({
        "user_id": "00000000-0000-0000-0000-000000000001",
        "symptom": "Headache",
        "mood": "😞",
        "severity": 7,
    }).encode(),
    headers={'Content-Type': 'application/json'},
)
resp = urllib.request.urlopen(req)
data = json.loads(resp.read().decode())
print("\nDIARY add:")
print(json.dumps(data, indent=2))
