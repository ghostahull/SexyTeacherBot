import random
import re
import sqlite3

VIDEO_FORMAT = re.compile("^http(?:s?)://(?:www\.)?youtu(?:be\.com/watch\?v=|\.be/)([\w\-_]*)(&(amp;)?‌​[\w\?‌​=]*)?$")


class Learninghub(object):
    def __init__(self, data, bot):
        self.name = "#learninghub"
        self.data = data
        self.bot = bot
        self.db = sqlite3.connect("db.sqlite3")
        self.c = self.db.cursor()

    def welcome(self, nick):
        greet = (
            "Welcome to #learninghub %s! Here you'll find lots of resources and people to learn hacking/pentesting "
            "as well as other IT subjects. Type ?goldmine to get started and get rid of the welcome message. Type "
            "?desc <course_number> to know the description of a course. You have to use the course number in the "
            "ghostbin. Type ?help for more." % nick
        )

        sha2 = self.bot.sha2(nick)
        self.c.execute("SELECT count(*) FROM users WHERE hash=?", sha2)

        if not self.c.fetchone()[0]:
            self.c.execute("INSERT into users (hash) values (?)", sha2)
            self.db.commit()
            self.bot.notice(nick, greet)

    def users(self, nick=None):
        self.c.execute("SELECT count(*) FROM users")
        count = self.c.fetchone()[0]
        msg = "There are %d registered users." % count
        return self.bot.check_nick(msg, nick)

    def random_course(self, nick=None):
        self.c.execute("SELECT * FROM main_course")
        course = random.choice(self.c.fetchall())
        msg = "%s. %s." % (course[4], course[1])
        return self.bot.check_nick(msg, nick)

    def desc(self, course):
        try:
            self.c.execute("SELECT * FROM main_course WHERE key=?", course)
            return self.c.fetchone()[2]
        except:
            return "?desc <1-133>"

    def link(self, course):
        try:
            self.c.execute("SELECT * FROM main_course WHERE key=?", course)
            return self.c.fetchone()[3]
        except:
            return "?link <1-133>"

    def whatof(self, arg=None):
        if arg in self.data[self.name]["whatof"]:
            return self.data[self.name]["whatof"][arg]
        else:
            return "There is no data for this user."


class Opsec(object):
    def __init__(self, data, bot):
        self.data = data
        self.bot = bot
        self.name = "#opsec"

    def video(self, nick=None):
        videos = self.data[self.name]["videos"]
        return self.bot.check_nick(random.choice(videos), nick)

    def add_video(self, video=None):
        if video in self.data[self.name]["videos"]:
            return "Video already exists."

        if not VIDEO_FORMAT.match(video):
            return "Wrong video format. Please add youtube links only."

        self.data[self.name]["videos"].append(video)
        self.bot.write_data(self.data)
        return "Video added successfully."
