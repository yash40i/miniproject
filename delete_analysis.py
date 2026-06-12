import sqlite3

conn = sqlite3.connect('./analysis.db')
cursor = conn.cursor()

# Delete the problematic analysis and related records
cursor.execute('DELETE FROM feedback WHERE analysis_id = ?', ('708aa6f9-24d4-4997-a706-7aeae04b6da8',))
cursor.execute('DELETE FROM matching_results WHERE analysis_id = ?', ('708aa6f9-24d4-4997-a706-7aeae04b6da8',))
cursor.execute('DELETE FROM learning_paths WHERE analysis_id = ?', ('708aa6f9-24d4-4997-a706-7aeae04b6da8',))
cursor.execute('DELETE FROM analyses WHERE id = ?', ('708aa6f9-24d4-4997-a706-7aeae04b6da8',))

conn.commit()
print("Deleted old analysis records")
conn.close()
