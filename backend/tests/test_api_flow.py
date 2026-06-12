import json
import requests
from pathlib import Path

print('🔐 Testing Complete API Flow')
print('=' * 60)

# Test 1: Sign up new user
print('[1] Creating test user account...')
signup_data = {
    'email': 'test.user@example.com',
    'password': 'TestPass123!',
    'full_name': 'Test User'
}

try:
    response = requests.post('http://localhost:8000/auth/signup', json=signup_data)
    print(f'   Status: {response.status_code}')
    if response.status_code == 201:
        user_id = response.json()['user_id']
        print(f'   ✅ User created: {user_id}')
    elif response.status_code == 400:
        print(f'   ℹ️  User may already exist')
    else:
        print(f'   Response: {response.text[:200]}')
except Exception as e:
    print(f'   Error: {str(e)[:100]}')

print()

# Test 2: Login
print('[2] Logging in...')
login_data = {
    'email': 'test.user@example.com',
    'password': 'TestPass123!'
}

try:
    response = requests.post('http://localhost:8000/auth/login', json=login_data)
    print(f'   Status: {response.status_code}')
    if response.status_code == 200:
        token = response.json()['access_token']
        print(f'   ✅ Logged in, token: {token[:20]}...')
    else:
        print(f'   Response: {response.text[:200]}')
        token = None
except Exception as e:
    print(f'   Error: {str(e)[:100]}')
    token = None

print()

# Test 3: Get current user
if token:
    print('[3] Getting current user...')
    headers = {'Authorization': f'Bearer {token}'}

    try:
        response = requests.get('http://localhost:8000/auth/me', headers=headers)
        print(f'   Status: {response.status_code}')
        if response.status_code == 200:
            user = response.json()
            print(f'   ✅ Current user: {user["email"]}')
        else:
            print(f'   Response: {response.text[:200]}')
    except Exception as e:
        print(f'   Error: {str(e)[:100]}')

    print()

    # Test 4: Upload resume and analyze
    print('[4] Uploading resume for analysis...')
    pdf_file = Path('sample_resume.pdf')
    job_desc = Path('sample_job.txt').read_text()

    try:
        with open(pdf_file, 'rb') as f:
            files = {'file': f}
            data = {'job_description': job_desc}
            response = requests.post(
                'http://localhost:8000/api/analyze',
                headers=headers,
                files=files,
                data=data
            )
        
        print(f'   Status: {response.status_code}')
        if response.status_code == 202:
            result = response.json()
            analysis_id = result['analysis_id']
            print(f'   ✅ Analysis queued: {analysis_id}')
            print(f'      Status: {result["status"]}')
        else:
            print(f'   Response: {response.text[:300]}')
    except Exception as e:
        print(f'   Error: {str(e)[:100]}')

    print()

print('✅ API Flow Test Complete!')
