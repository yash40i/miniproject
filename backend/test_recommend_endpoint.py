import requests
import json

url = "http://localhost:8000/api/recommend-courses"
data = {
    "job_description": "We are looking for a Backend Engineer with experience in Python, FastAPI, Docker, and AWS Cloud.",
    "experience_level": "beginner"
}

print("Sending request to /api/recommend-courses...")
try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("Success! Response:")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Failed: {response.text}")
except Exception as e:
    print(f"Error: {e}")
