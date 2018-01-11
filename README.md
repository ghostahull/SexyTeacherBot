# SexyTeacherBot

> Project must be run with python3.6

This bot's main aim is to have an easy-to-modify structure, so that plugins can be easily.

## Code

The code is structured in three main files.
1. **Bot.py**: contains the bot's inner workings, it takes care of sockets and connections.
2. **main.py**: is one level higher than Bot.py. It mainly interacts with Bot.py, stating how the
bot should respond, and links all plugins together.

### Plugins

3. **CustomChannels.py** controls plugins. A plugin is a class referencing a channel's name. It's 
structure should follow the structure below:

```
class Channel_name(object):
    def __init__(self, data, bot):
        self.name = "#channel_name"
        self.data = data
        self.bot = bot
        
    def shout(self, arg=None):
        """ An example of an action, it should return a response. The arg is optional. """
        if arg:
            return "HELLO %s!" % arg.upper()
        
        return "HELLO!"
```

Actions should only be used for answers that need some kind of computation. If it is 
a static response it should be added to the conf.json following the structure below:

```
'conf' = {
    "#channel_name": {
        "commands": {
            "hello": "Hello"  # Answers `Hello` when someone executes `?hello`.
        },
        "actions": {
            "shout": "shout"  # Points the command `?shout` to the function `shout`.
        },
        "help": {
            "shout": "Use ?shout <nick>"  # Return custom help for an action: `?help shout`.
        }
    }
}
```

## Config file

This file is not included in the repository and must be added. Each channel should have 
an entry as showed above. 

```
{
    'conf' = {
        "irc": str(),       # IRC's address
        "port": int(),      # IRC's port
        "nick": str(),      # Bot's nick
        "user": str(),      # Bot's username
        "real": str(),      # Bot's realname
        "pass": str()       # Bot's password
        "chans": [str()],   # Channels to connect to
    }
}
```
