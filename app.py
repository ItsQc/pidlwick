# app.py
#
# The main entrypoint to the Pidlwick Discord bot for the Enter Ravenloft server.
# Sets up the periodic background tasks to refresh shop inventory and registers
# a handler for all bot commands.

import discord
import os
import yaml
import logging
import logging.config

from client import Client
from dotenv import load_dotenv

 # Read environment variables from .env (does not overwrite existing value)
load_dotenv() 

# Configure logging for the app and discord.py library
with open('logging.yml', 'r') as f:
    logging_config = yaml.safe_load(f)

logging.config.dictConfig(logging_config)

# Configure intents AKA Discord API capabilities
intents = discord.Intents.default()
intents.message_content = True  # For reacting to messages
intents.members = True  # For iterating over guild.members
client = Client(intents=intents)

# Start the bot
bot_token = os.environ['DISCORD_BOT_TOKEN']
if bot_token:
    client.run(bot_token, log_handler=None)
else:
    raise RuntimeError('The DISCORD_BOT_TOKEN environment variable must be set (try .env for local development)')
