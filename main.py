from threading import Thread
import json

from lib.Bot import Bot
from lib.Exceptions import InvalidConfiguration


ART = """
   _____              _______              _               ____        _
  / ____|            |__   __|            | |             |  _ \      | |
 | (___   _____  ___   _| | ___  __ _  ___| |__   ___ _ __| |_) | ___ | |_
  \___ \ / _ \ \/ / | | | |/ _ \/ _` |/ __| '_ \ / _ \ '__|  _ < / _ \| __|
  ____) |  __/>  <| |_| | |  __/ (_| | (__| | | |  __/ |  | |_) | (_) | |_
 |_____/ \___/_/\_\\__, |_|\___|\__,_|\___|_| |_|\___|_|  |____/ \___/ \__|
                    __/ |
                   |___/
                                  Special thanks to ClaudiaD & l33t
"""


def load_config():
    CONF_FILE = "conf.json"

    try:
        f = open(CONF_FILE, 'r')
        data = json.load(f)
    except Exception:
        raise InvalidConfiguration

    return data


def main():
    # print(ART)
    data = load_config()
    bot = Bot(data)
    Thread(target=bot.chat).start()

    print("[+] Bot is up and running.")
    print(bot.conf["chans"][0])

    bot.run()


if __name__ == "__main__":
    main()
