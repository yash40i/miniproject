import sqlite3

conn = sqlite3.connect('analysis.db')
cursor = conn.cursor()

print('🔧 Migrating database...')

# Add user_id column if it doesn't exist
try:
    cursor.execute("ALTER TABLE analyses ADD COLUMN user_id INTEGER")
    conn.commit()
    print('✅ Added user_id column to analyses table')
except sqlite3.OperationalError as e:
    if 'duplicate column name' in str(e):
        print('ℹ️  user_id column already exists')
    else:
        print(f'Error: {e}')

# Verify the schema
print()
print('📊 Updated Analyses Table Schema:')
cursor.execute("PRAGMA table_info(analyses)")
columns = cursor.fetchall()
for col in columns:
    print(f'  {col[1]}: {col[2]}')

conn.close()
