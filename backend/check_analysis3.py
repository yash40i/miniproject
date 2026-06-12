import sqlite3

conn = sqlite3.connect('./analysis.db')
cursor = conn.cursor()

analysis_id = "ad16d797-e1b1-49fc-8488-992e08f56508"

# Check Analysis
cursor.execute('SELECT id, status FROM analyses WHERE id = ?', (analysis_id,))
result = cursor.fetchone()
print(f'Analysis: {result}')

# Check Feedback
cursor.execute('SELECT analysis_id FROM feedback WHERE analysis_id = ?', (analysis_id,))
result = cursor.fetchone()
print(f'Feedback: {result}')

# Check MatchingResult
cursor.execute('SELECT analysis_id FROM matching_results WHERE analysis_id = ?', (analysis_id,))
result = cursor.fetchone()
print(f'MatchingResult: {result}')

conn.close()
