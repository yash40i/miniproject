import json
import time
import requests
from pathlib import Path

# Login and get token
login_data = {
    'email': 'test.user@example.com',
    'password': 'TestPass123!'
}

response = requests.post('http://localhost:8000/auth/login', json=login_data)
token = response.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

# Analysis ID from previous test
analysis_id = '26c1dd73-53ec-44c2-a67a-b50ebfd95c8c'

print('📊 Polling Analysis Results')
print('=' * 60)
print(f'Analysis ID: {analysis_id}')
print()

# Poll for results
for attempt in range(1, 13):
    response = requests.get(
        f'http://localhost:8000/api/results/{analysis_id}',
        headers=headers
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f'[Attempt {attempt}] Status: {result["status"]}')
        
        if result['status'] == 'completed':
            print()
            print('✅ ANALYSIS COMPLETED!')
            print()
            print('📈 Results:')
            print(f'  Overall Match Score: {result["overall_score"]:.1f}%')
            print(f'  Matched Skills: {result["matched_count"]}')
            print(f'  Missing Skills: {result["missing_count"]}')
            
            if 'feedback' in result:
                feedback = result['feedback']
                print()
                print('📝 Feedback:')
                print(f'  Gap Analysis: {feedback["gap_analysis"][:200]}...')
                print()
                print(f'  Recommendations ({len(feedback["recommendations"])} items):')
                for i, rec in enumerate(feedback['recommendations'][:3], 1):
                    print(f'    {i}. {rec}')
                print()
                print(f'  Priority Skills: {feedback["priority_skills"]}')
                print()
                print('🎓 Learning Path:')
                if 'milestones' in feedback:
                    for milestone in feedback['milestones'][:2]:
                        print(f'  - {milestone}')
            
            break
        elif result['status'] == 'failed':
            print(f'  Error: {result["error"]}')
            break
    else:
        print(f'[Attempt {attempt}] Status: {response.status_code}')
    
    if attempt < 12:
        print('  Waiting 2 seconds...')
        time.sleep(2)
else:
    print()
    print('⏱️  Analysis still processing after 24 seconds')

print()
print('✅ Test Complete!')
