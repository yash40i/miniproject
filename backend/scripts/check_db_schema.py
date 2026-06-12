import sqlite3

conn = sqlite3.connect('analysis.db')
cursor = conn.cursor()

# Check analyses table schema
print('📊 Current Analyses Table Schema:')
try:
    cursor.execute("PRAGMA table_info(analyses)")
    columns = cursor.fetchall()
    for col in columns:
        print(f'  {col[1]}: {col[2]}')
except:
    print("  Table does not exist")

print()
print('Checking all tables:')
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
for table in tables:
    print(f'  - {table[0]}')

conn.close()
