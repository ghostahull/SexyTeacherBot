#!/usr/bin/python

import asyncio
import hashlib
import re
import socket
import ssl

__author__ = "Anonymous"
__license__ = "GPLv3"

CONF_FILENAME = "conf.json"


loop = asyncio.get_event_loop()

def exe(coro):
    return loop.run_until_complete(coro)


class Bot(object):
    def __init__(self, data):
        self.data = data
        self.conf = data["conf"]
        self.s = None
        exe(self.bootstrap())

    @staticmethod
    def sha2(text):
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    async def bootstrap(self):
        await self.connect()
        await self.auth()
        await self.ping()
        await self.join()

    async def connect(self):
        try:
            print("[*] Connecting to server.")
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 0)
            self.s.setblocking(True)
            self.s = ssl.wrap_socket(self.s)
            await asyncio.sleep(1)
            self.s.connect((self.conf["irc"], self.conf["port"]))
            await asyncio.sleep(1)
        except Exception as e:
            print("Failed to connect. %s:%d" % (self.conf["irc"], self.conf["port"]))
            print(e)
            exit()

    async def auth(self):
        print("[+] Sending credentials for %s." % self.conf["nick"])

        if self.conf["pass"]:
            self.send("PASS %s\r\n" % self.conf["pass"])

        self.send("NICK %s\r\n" % self.conf["nick"])
        self.send("USER %s 0 * :%s\r\n" % (
            self.conf["user"],
            self.conf["real"]
        ))
        print("[+] Credentials sent. Waiting for authentication.")
        await asyncio.sleep(1)

    async def login(self):
        self.send(":source PRIVMSG nickserv :identify %s\r\n" % self.conf["pass"])
        await asyncio.sleep(1)

    async def join(self):
        print("[+] Joining channels.\n")

        # Ensure the login is made correctly.
        # Most times the first login doesn't connect.
        for _ in range(3):
            await self.login()

        for x in self.conf["chans"]:
            self.send("JOIN %s\r\n" % x)

        self.send("MODE %s +B\r\n" % self.conf["nick"])
        await asyncio.sleep(1)

    async def ping(self):
        while True:
            try:
                recvd = self.s.recv(4096).decode()

                if "PING" in recvd:
                    await self.pong(recvd)
                elif "%s!%s" % (self.conf["nick"], self.conf["user"]) in recvd:
                    print("[+] Ping successfully completed.")
                    break

            except socket.timeout:
                raise ("[-] Error: ", socket.timeout)

        await asyncio.sleep(1)

    async def pong(self, msg):
        self.send("PONG %s\r\n" % msg.split()[1])

    async def listen(self):
        valid = re.compile(
            r"^:(?P<nick>\w+)!\S* (?P<mode>[A-Z]+) :?(?P<chan>#?\w+)(\s:\?(?P<cmd>\w+)(\s(?P<arg>\w+))?)?")

        recvd = self.s.recv(4096).decode()

        if "PING" in recvd:
            await self.pong(recvd)
            return

        data = valid.match(recvd)

        if not data:
            return

        nick = data.group("nick")
        mode = data.group("mode")
        chan = data.group("chan")
        cmd = data.group("cmd")
        arg = data.group("arg")

        # Allow the bot to have private conversations
        if chan == self.conf["nick"]:
            chan = nick
        elif chan:
            chan = chan.lower()

        # Send welcome message to new users
        if mode == "JOIN":
            cmd, arg = "welcome", nick

        if isinstance(cmd, str):
            msg = "<%s:%s> %s" % (nick, chan, cmd)
            if arg:
                msg += " " + arg
            print(msg)
            return nick, chan, cmd, arg

    def send(self, msg):
        self.s.send(msg.encode("UTF-8"))

    def message(self, msg, chan):
        self.send("PRIVMSG %s :%s\r\n" % (chan, msg))

    def notice(self, user, msg):
        self.send("NOTICE %s :%s\r\n" % (user, msg))

    @staticmethod
    def check_nick(msg, nick=None):
        return "%s: %s" % (nick, msg) if nick else msg
