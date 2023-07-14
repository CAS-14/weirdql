import wql

class User(wql.Model):
    _tablename = "users"

    uid = wql.Col("integer", primary=True)
    username = wql.Col("text", null=False, unique=True)
    pwhash = wql.Col("text", null=False)
    level = wql.Col("int", null=False)
    created = wql.Col("int", null=False)
    last_login = wql.Col("int")
    first_ip = wql.Col("text")
    last_ip = wql.Col("text")
    referrer = wql.Col("text", foreign_key="User.uid")

db = wql.Database("test.db", User)

db.insert(User(username="bob", pwhash="hi", level=10, created=1776))

db.select_all(User, "level>5")
db.select_only(User, "username=bob")
db.select_one(User, order=wql.ord_random)

