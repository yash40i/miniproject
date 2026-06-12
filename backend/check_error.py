import sqlite3

conn = sqlite3.connect('./analysis.db')
cursor = conn.cursor()

analysis_id = "31c34829-23e8-4cd8-a363-135490ca1072"

# Check Analysis error
cursor.execute('SELECT id, status, error FROM analyses WHERE id = ?', (analysis_id,))
result = cursor.fetchone()
print(f'Analysis status: {result}')

if result and result[2]:  # if error exists
    print(f'\nError details:\n{result[2]}')

conn.close()
