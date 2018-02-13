import json
from threading import Thread

from lib import CustomChannels
from lib.Bot import Bot

CONF_FILE_NAME = "conf.json"


def main():
    global bot
    data = load_config()
    bot = Bot(data)
    Thread(target=chat).start()

    print("[+] bot is up and running.")
    print(bot.conf["chans"][0])

    while True:
        listen()


def load_config():
    f = open(CONF_FILE_NAME, 'r')
    data = json.load(f)
    return data


def write_data(data):
    w = open(CONF_FILE_NAME, "w")
    json.dump(data, w)
    w.close()


def chat():
    while True:
        bot.message(input(), bot.conf["chans"][0])


def find(path):
    data = bot.data

    for subpath in path:
        if subpath not in data:
            return False

        data = data[subpath]

    return data


def bot_help(chan=None, arg=None):
    if find([chan, "help", arg]):
        return find([chan, "help", arg])
    elif find(["commands", arg]):
        return "Quick response command. Use: ?%s <nick>" % arg.lower()

    commands = [key for key in bot.data["commands"].keys()]

    if find([chan, "commands"]):
        cmds = bot.data[chan]["commands"]
        commands.extend([key for key in cmds.keys()])

        if arg in cmds:
            return "Quick response command. Use: ?%s <nick>" % arg.lower()

    if find([chan, "actions"]):
        acts = bot.data[chan]["actions"]

        # Commands lower than 3 characters are shortcuts, therefore not a command.
        commands.extend([cmd for cmd in acts if len(cmd) > 3])

        if arg in acts:
            return "Command has no help. Try: ?%s" % arg.lower()

    commands.sort()
    cmds = ", ".join("?%s" % x for x in commands)
    msg = "Available commands: \u0002%s\u000F." % cmds
    return bot.check_nick(msg, arg)


def listen():
    info = bot.listen()

    if not info:
        return

    nick, chan, cmd, arg = info
    response = "The command you are trying to execute does not exist."

    if cmd == "help" or cmd == "h":
        response = bot_help(chan, arg)
    elif find(["commands", cmd]):
        response = bot.check_nick(find(["commands", cmd]), arg)
    elif find([chan, "commands", cmd]):
        response = bot.check_nick(find([chan, "commands", cmd]), arg)
    elif find([chan, "actions", cmd]) and hasattr(CustomChannels, chan[1:].title()):
        void = str(bot.data[chan]["actions"][cmd])
        obj = getattr(CustomChannels, chan[1:].title())(bot.data, bot)
        response = exec_command(obj, void, arg)

    if response and cmd != "welcome":
        bot.message(response, chan)


def exec_command(obj, void, arg):
    response = "That is not a valid command format."

    if hasattr(obj, void):
        func = getattr(obj, void)
        response = func(arg) if arg else func()

    return response


if __name__ == "__main__":
    main()
