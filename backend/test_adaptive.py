import requests
import json

data = {
    'analysis_id': '4307124f-fd9e-412f-a1f6-147575d739e5',
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
if response.status_code == 200:
    result = response.json()
    lp = result.get('learning_path', {})
    print('SUCCESS!')
    print(f'Adaptivity Score: {lp.get("adaptivity_score", "N/A")}')
    print(f'Total Hours: {lp.get("total_hours", "N/A")}')
    print(f'Milestones: {len(lp.get("milestones", []))}')
    
    # Show milestone titles
    milestones = lp.get('milestones', [])
    print('\nMilestones:')
    for i, m in enumerate(milestones, 1):
        print(f'  {i}. {m.get("title", "N/A")} ({m.get("difficulty", "N/A")})')
else:
    print(f'Error: {response.json()}')
