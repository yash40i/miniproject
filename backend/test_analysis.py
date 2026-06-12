import requests
import os

# Read sample resume PDF
with open('sample_resume.pdf', 'rb') as f:
    resume_content = f.read()

# Prepare the multipart request
files = {
    'file': ('sample_resume.pdf', resume_content, 'application/pdf'),
}
data = {
    'job_description': 'Senior Python Developer - 5+ years experience required. Must have expertise in FastAPI, PostgreSQL, Docker, AWS, and machine learning pipelines. Experience with production systems, CI/CD, and team leadership preferred.'
}

# Make the request
response = requests.post(
    'http://localhost:8000/api/analyze',
    files=files,
    data=data
)

print(f"Status: {response.status_code}")
result = response.json()
print(f"Analysis ID: {result.get('analysis_id')}")
print(f"Status: {result.get('status')}")
