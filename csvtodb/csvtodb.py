import sqlite3
import csv

conn = sqlite3.connect('jobs_database.db')
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    processed_job_title TEXT,
    processed_job_description TEXT
)
''')

with open('processed_data.csv', 'r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        cursor.execute('''
            INSERT INTO jobs (processed_job_title, processed_job_description)
            VALUES (?, ?)
        ''', (row['Processed_Job_Title'], row['Processed_Job_Description']))
conn.commit()
conn.close()
print("CSV data uploaded successfully into SQLite database!")
