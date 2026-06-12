import sqlite3

conn = sqlite3.connect('./analysis.db')
cursor = conn.cursor()

analysis_id = "708aa6f9-24d4-4997-a706-7aeae04b6da8"

# Check Analysis
cursor.execute('SELECT id, status FROM analyses WHERE id = ?', (analysis_id,))
result = cursor.fetchone()
print(f'Analysis found: {result}')

# Check Feedback
cursor.execute('SELECT analysis_id FROM feedback WHERE analysis_id = ?', (analysis_id,))
result = cursor.fetchone()
print(f'Feedback found: {result}')

# Check MatchingResult
cursor.execute('SELECT analysis_id FROM matching_results WHERE analysis_id = ?', (analysis_id,))
result = cursor.fetchone()
print(f'MatchingResult found: {result}')

conn.close()
