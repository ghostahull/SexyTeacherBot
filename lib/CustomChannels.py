import random
import sqlite3
import psycopg2


class Learninghub(object):
    def __init__(self, data, bot):
        self.name = "#learninghub"
        self.data = data
        self.bot = bot
        self.courses_db = psycopg2.connect(
            "host='ec2-23-21-186-138.compute-1.amazonaws.com'"
            "dbname='d5h8kcam6auolb'"
            "user='ulsqobzojookfh'"
            "password=''"
        )
        self.users_db = sqlite3.connect("users.sqlite3")

    def welcome(self, nick):
        greet = (
                "Welcome to #learninghub, %s! Here you'll find lots of resources and people "
                "to learn hacking/pentesting as well as other IT subjects. Type ?goldmine to "
                "check out all of our courses. ?website would link you to an easy to use site "
                "for the courses. Type ?help for more." % nick
        )

        sha2 = self.bot.sha2(nick)
        c = self.users_db.cursor()
        c.execute("SELECT count(*) FROM users WHERE hash=?", (sha2,))

        if c.fetchone()[0] == 0:
            c.execute("INSERT into users (hash) values (?)", (sha2,))
            self.users_db.commit()
            self.bot.notice(nick, greet)

    def users(self, nick=None):
        c = self.users_db.cursor()
        c.execute("SELECT count(*) FROM users")
        count = c.fetchone()[0]
        msg = "There are %d registered users." % count
        return self.bot.check_nick(msg, nick)

    def desc(self, course):
        c = self.courses_db.cursor()
        try:
            c.execute("SELECT * FROM main_course WHERE key=%s", (course,))
            return c.fetchone()[2]
        except:
            return "?desc <1-133>"

    def link(self, course):
        c = self.courses_db.cursor()
        try:
            c.execute("SELECT * FROM main_course WHERE key=%s", (course,))
            return c.fetchone()[3]
        except:
            return "?link <1-133>"

    def random_course(self, nick=None):
        c = self.courses_db.cursor()
        c.execute("SELECT * FROM main_course")
        course = random.choice(c.fetchall())
        msg = "%s. %s." % (course[4], course[1])
        return self.bot.check_nick(msg, nick)

    def whatof(self, arg=None):
        if arg in self.data[self.name]["whatof"]:
            return self.data[self.name]["whatof"][arg]
        else:
            return "There is no data for this user."
