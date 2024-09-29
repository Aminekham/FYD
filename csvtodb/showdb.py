import sqlite3

conn = sqlite3.connect('jobs_database.db')
cursor = conn.cursor()
cursor.execute('SELECT * FROM jobs')
rows = cursor.fetchall()
print("ID | Processed Job Title | Processed Job Description")
print("-" * 50)
for row in rows:
    print(f"{row[0]} | {row[1]} | {row[2]}...")
conn.close()
