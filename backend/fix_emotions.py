import sqlite3

conn = sqlite3.connect("journals.db")
cursor = conn.cursor()
cursor.execute("UPDATE journal_entries SET emotion=NULL, keywords=NULL, summary=NULL WHERE emotion='unknown'")
rows = cursor.rowcount
conn.commit()
conn.close()
print(f"Cleared {rows} entries with unknown emotion. Please re-analyze them in the app.")
