import json
from threading import Thread

from lib.Bot import Bot
from lib.Exceptions import InvalidConfiguration


def load_config():
    CONF_FILE = "conf.json"

    try:
        f = open(CONF_FILE, 'r')
        data = json.load(f)
    except Exception:
        raise InvalidConfiguration

    return data


def main():
    data = load_config()
    bot = Bot(data)
    Thread(target=bot.chat).start()

    print("[+] Bot is up and running.")
    print(bot.conf["chans"][0])

    bot.run()


if __name__ == "__main__":
    main()
