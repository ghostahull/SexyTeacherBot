import sqlite3

db = sqlite3.connect("/home/alpha/Documents/1/Websites/Django/learninghub/db.sqlite3")
c = db.cursor()
c.execute("SELECT * FROM main_course WHERE key=?", ("1",))

print(c.fetchone())
