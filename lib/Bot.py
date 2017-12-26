#!/usr/bin/python

import hashlib
import json
import re
import socket
import ssl
from time import sleep

import lib.CustomChannels as CustomChannels

__author__ = "Anonymous"
__license__ = "GPLv3"

CONF_FILENAME = "conf.json"


class Bot(object):
    def __init__(self, data):
        self.data = data
        self.conf = data["conf"]
        self._bootstrap()

    @staticmethod
    def sha2(text):
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def _bootstrap(self):
        self.s = None
        self.running = True
        self._connect()
        sleep(1)
        self.auth()
        self.ping()
        sleep(3)
        self.join()

    def _connect(self):
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 0)
            self.s.setblocking(1)
            self.s = ssl.wrap_socket(self.s)
            self.s.connect((self.conf["irc"], self.conf["port"]))
        except Exception as e:
            print("Failed to connect. %s:%d" % (self.conf["irc"], self.conf["port"]))
            print(e)
            exit()

    def _send(self, msg):
        self.s.send(msg.encode("UTF-8"))

    def _listen(self):
        valid = re.compile(
            r"^:(?P<nick>\w+)!\S* (?P<mode>[A-Z]+) :?(?P<chan>#?\w+)(\s:\?(?P<cmd>\w+)(\s(?P<arg>\w+))?)?")

        recvd = self.s.recv(4096).decode()

        if "PING" in recvd:
            self.pong(recvd)
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

    def message(self, msg, chan):
        self._send("PRIVMSG %s :%s\r\n" % (chan, msg))

    def notice(self, user, msg):
        self._send("NOTICE %s :%s\r\n" % (user, msg))

    def auth(self):
        print("[+] Sending credentials for %s." % self.conf["nick"])

        if self.conf["pass"]:
            self._send("PASS %s\r\n" % self.conf["pass"])

        self._send("NICK %s\r\n" % self.conf["nick"])
        self._send("USER %s 0 * :%s\r\n" % (
            self.conf["user"],
            self.conf["real"]
        ))
        print("[+] Credentials sent. Waiting for authentication.")

    def ping(self):
        while True:
            try:
                recvd = self.s.recv(4096).decode()

                if "PING" in recvd:
                    self.pong(recvd)
                elif "%s!%s" % (self.conf["nick"], self.conf["user"]) in recvd:
                    print("[+] Ping successfully completed.")
                    break
                else:
                    break

            except socket.timeout:
                raise ("[-] Error: ", socket.timeout)

    def pong(self, msg):
        self._send("PONG %s\r\n" % msg.split()[1])

    def login(self):
        self._send(":source PRIVMSG nickserv :identify %s\r\n" % self.conf["pass"])

    def join(self):
        print("[+] Joining channels.\n")

        # Ensure the login is made correctly.
        # Most times the first login doesn't connect.
        [self.login() for _ in range(3)]

        for x in self.conf["chans"]:
            self._send("JOIN %s\r\n" % x)

        self._send("MODE %s +B\r\n" % self.conf["nick"])

    def run(self):
        while self.running:
            try:
                self.listen()
            except Exception as e:
                print("Exception: %s" % str(e))
                print("Sleeping 5 seconds before reconnecting.")
                sleep(5)
                self._bootstrap()

    def chat(self):
        while True:
            msg = input()
            self.message(msg, self.conf["chans"][0])

    def bot_help(self, chan=None, arg=None):
        if chan in self.data \
                and "help" in self.data[chan] \
                and arg in self.data[chan]["help"]:
            return self.data[chan]["help"][arg]

        if arg in self.data["commands"]:
            return "Quick response command. Use: ?%s <nick>" % arg.lower()

        commands = [x for x in self.data["commands"]]
        if chan in self.data:
            if "commands" in self.data[chan]:
                if arg in self.data[chan]["commands"]:
                    return "Quick response command. Use: ?%s <nick>" % arg.lower()
                commands += [x for x in self.data[chan]["commands"]]

        if chan in self.data and "actions" in self.data[chan]:
            if arg in self.data[chan]["actions"]:
                return "There is no help for that command. Try: ?%s" % arg.lower()

            commands += [x for x in self.data[chan]["actions"] if len(x) > 3]

        commands.sort()
        cmds = ", ".join("?%s" % x for x in commands)
        msg = "Available commands: \u0002%s\u000F." % cmds
        return self.check_nick(msg, arg)

    def listen(self):
        info = self._listen()

        if not info:
            return

        nick, chan, cmd, arg = info
        response = "The command you are trying to execute does not exist."

        if cmd == "help" or cmd == "h":
            response = self.bot_help(chan, arg)
        elif cmd in self.data["commands"]:
            response = self.check_nick(self.data["commands"][cmd], arg)
        elif chan in self.data:
            if cmd in self.data[chan]["commands"]:
                response = self.check_nick(
                    self.data[chan]["commands"][cmd], arg
                )
            elif cmd in self.data[chan]["actions"] and \
                    hasattr(CustomChannels, chan[1:].title()):
                void = str(self.data[chan]["actions"][cmd])
                obj = getattr(CustomChannels, chan[1:].title())(self.data, self)
                response = self.exec_command(obj, void, arg)

        if response and cmd != "welcome":
            self.message(response, chan)

    @staticmethod
    def exec_command(obj, void, arg):
        try:
            func = getattr(obj, void)
            response = func(arg) if arg else func()
        except Exception:
            response = "That is not a valid command format."
        return response

    @staticmethod
    def write_data(data):
        w = open(CONF_FILENAME, "w")
        json.dump(data, w)
        w.close()

    @staticmethod
    def check_nick(msg, nick=None):
        return "%s: %s" % (nick, msg) if nick else msg