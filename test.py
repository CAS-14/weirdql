import wql
import sqlite3
import os

if os.path.isfile("test.db"):
    os.remove("test.db")

with open("/home/cas/code/flask-sites/utility/schemas/channel.sql", "r") as f:
    init_script = f.read()

con = sqlite3.connect("test.db")
cur = con.cursor()
cur.executescript(init_script)
con.commit()
con.close()

db = wql.Database("test.db")