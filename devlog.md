# DevLog

Writing down what I did so that maybe I or others can replicate it.

## Setup Python environment

(These commands are for Mac.)

Ensure Python3 and pip are installed

Get the [python-dotenv](https://pypi.org/project/python-dotenv/) library: `pip install python-dotenv`

Get the [discord.py](https://discordpy.readthedocs.io/en/latest/index.html) library: `pip install -U discord.py`


## Create Discord Application

Follow the Discord [developer docs](https://discord.com/developers/docs/getting-started)

[Developer Dashboard](https://discord.com/developers/applications) -> **New Application**
Fill out name & description.

**Bot** -> **Add Bot**
Fill out name (Pidlwick II) and icon.
Click **Reset Token**.
```
IMPORTANT: Keep the token secret (password manager) and never check it into git. 
```

### Bot Configuration

**Privileged Gateway Intents** -> enable "Message Content Intent"


## Installing the Bot


