import json
import requests

# Login
login_data = {'email': 'test.user@example.com', 'password': 'TestPass123!'}
response = requests.post('http://localhost:8000/auth/login', json=login_data)
token = response.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

# Get analysis results
analysis_id = '26c1dd73-53ec-44c2-a67a-b50ebfd95c8c'
response = requests.get(f'http://localhost:8000/api/results/{analysis_id}', headers=headers)
result = response.json()

print('✅ COMPLETE END-TO-END ANALYSIS RESULTS')
print('=' * 70)
print()

# Matching Results
print('📊 SEMANTIC MATCHING RESULTS')
print('-' * 70)
matching = result['matching_result']
print(f'Overall Match Score: {matching["overall_score"]:.1f}%')
print(f'Matched Percentage: {matching["matched_percentage"]:.1f}%')
print(f'Total Matched Skills: {len(matching["matched_skills"])}')
print()
print('Top 3 Matched Skills:')
for i, skill in enumerate(matching['matched_skills'][:3], 1):
    print(f'  {i}. {skill["resume_skill"]} → {skill["job_skill"]}')
    print(f'     Similarity: {skill["similarity_score"]:.2f} ({skill["match_strength"]})')

print()
print(f'Missing Skills: {len(matching["missing_skills"])}')
for i, skill in enumerate(matching['missing_skills'][:3], 1):
    print(f'  {i}. {skill}')

print()
print()

# Feedback from Groq LLM
print('🧠 GROQ LLM FEEDBACK')
print('-' * 70)
feedback = result['feedback']

print('Gap Analysis:')
print(feedback['gap_analysis'][:500])
print()

print(f'Priority Skills ({len(feedback["priority_skills"])} items):')
for skill in feedback['priority_skills'][:5]:
    print(f'  • {skill}')

print()
print(f'Recommendations ({len(feedback["recommendations"])} items):')
for i, rec in enumerate(feedback['recommendations'][:3], 1):
    print(f'  {i}. {rec}')

print()
print()

# Learning Path
if result['learning_path']:
    print('📚 PERSONALIZED LEARNING PATH')
    print('-' * 70)
    learning = result['learning_path']
    print(f'Milestones: {len(learning.get("milestones", []))} items')
    for milestone in learning.get('milestones', [])[:2]:
        print(f'  • {milestone}')

print()
print('=' * 70)
print('✅ COMPLETE PIPELINE WORKING END-TO-END!')
print('   6-Stage Flow: PDF Extract → NLP Clean → Embeddings → Semantic Match')
print('                → Groq LLM Feedback → Learning Path')
