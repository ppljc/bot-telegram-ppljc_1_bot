import sqlite3

conn = sqlite3.connect('server53.db')
cursor = conn.cursor()

cursor.execute("ALTER TABLE users RENAME COLUMN user_id TO id")
cursor.execute("ALTER TABLE users RENAME COLUMN username TO nickname")
cursor.execute("ALTER TABLE users RENAME COLUMN tgname TO username")

cursor.execute("ALTER TABLE users ADD COLUMN phone TEXT")

conn.commit()
conn.close()