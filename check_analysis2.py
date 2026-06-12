import sqlite3

conn = sqlite3.connect('./analysis.db')
cursor = conn.cursor()

analysis_id = "31c34829-23e8-4cd8-a363-135490ca1072"

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
