import requests
import json

data = {
    'analysis_id': 'ad16d797-e1b1-49fc-8488-992e08f56508',
    'user_profile': {
        'experience_level': 'intermediate',
        'learning_style': 'hands-on',
        'availability_hours_per_week': 15,
        'preferred_resource_types': ['Course', 'Tutorial'],
        'budget': 'free'
    }
}

response = requests.post('http://localhost:8000/api/learning-path/adaptive', json=data)
print(f'Status: {response.status_code}')
print(f'Full Response:')
print(json.dumps(response.json(), indent=2))
