import urllib.request

# Test bootstrap
req = urllib.request.Request(
    'http://127.0.0.1:8001/api/profile/bootstrap',
    method='POST',
    data=b'{}',
    headers={'Content-Type': 'application/json'},
)
resp = urllib.request.urlopen(req)
print("BOOTSTRAP:", resp.read().decode())

# Test GET profile
resp = urllib.request.urlopen('http://127.0.0.1:8001/api/profile/00000000-0000-0000-0000-000000000001')
print("PROFILE:", resp.read().decode())

# Test medical analyze
req = urllib.request.Request(
    'http://127.0.0.1:8001/api/medical/upload',
    method='POST',
    data=(
        b'--boundary\r\n'
        b'Content-Disposition: form-data; name="user_id"\r\n\r\n00000000-0000-0000-0000-000000000001\r\n'
        b'--boundary\r\n'
        b'Content-Disposition: form-data; name="title"\r\n\r\nBlood Test 2026\r\n'
        b'--boundary\r\n'
        b'Content-Disposition: form-data; name="record_type"\r\n\r\nblood_test\r\n'
        b'--boundary--\r\n'
    ),
    headers={'Content-Type': 'multipart/form-data; boundary=boundary'},
)
try:
    resp = urllib.request.urlopen(req)
    print("UPLOAD:", resp.read().decode())
except Exception as e:
    print("UPLOAD ERR:", e)
