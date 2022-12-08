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

import commands
import vistani_market
import tattoo_parlor

from dotenv import load_dotenv
from discord.ext import tasks

 # Read environment variables from .env (does not overwrite existing value)
load_dotenv() 

# Configure logging for the app and discord.py library
with open('logging.yml', 'r') as f:
    logging_config = yaml.safe_load(f)

logging.config.dictConfig(logging_config)

class Client(discord.Client):
    """
    The Client class leverages the Discord APIs to connect the bot to Discord,
    and from there to the target server(s).
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.log = logging.getLogger('app.Client')
        
        self.guild_name = os.environ['SERVER_NAME']
        self.vistani_channel_name = os.environ['VISTANI_MARKET_CHANNEL']
        self.tattoo_channel_name = os.environ['TATTOO_PARLOR_CHANNEL']

    async def setup_hook(self) -> None:
        self.refresh_vistani_market.start()
        self.refresh_tattoo_parlor.start()

    async def on_ready(self):
        self.log.info(f'Logged in as {self.user} (ID: {self.user.id}), guild="{self.guild_name}"')
        self.log.info('------')

    # Vistani Market background task
    @tasks.loop(time=vistani_market.REFRESH_TIME)
    async def refresh_vistani_market(self):
        # Why do the guild lookup here instead of in __init__? Because at init time it seems
        # like self.guilds is not populated yet. Maybe move this to `on_ready`?
        guild = discord.utils.get(self.guilds, name=self.guild_name)
        channel = discord.utils.get(guild.channels, name=self.vistani_channel_name)

        if vistani_market.should_refresh_today():
            output = vistani_market.generate_inventory()
            await vistani_market.post_inventory(output, channel)

    @refresh_vistani_market.before_loop
    async def before_refresh_vistani_market(self):
        await self.wait_until_ready()

    # Tattoo Parlor background task
    @tasks.loop(time=tattoo_parlor.REFRESH_TIME)
    async def refresh_tattoo_parlor(self):
        guild = discord.utils.get(self.guilds, name=self.guild_name)
        channel = discord.utils.get(guild.channels, name=self.tattoo_channel_name)

        if tattoo_parlor.should_refresh_today():
            output = tattoo_parlor.generate_inventory()
            await tattoo_parlor.post_inventory(output, channel)

    @refresh_tattoo_parlor.before_loop
    async def before_refresh_tattoo_parlor(self):
        await self.wait_until_ready()

intents = discord.Intents.default()
intents.message_content = True  # For reacting to messages

client = Client(intents=intents)

# Event listeners - route commands to the 'command' module
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    elif message.content.startswith(commands.PREFIX):
        await commands.handle(message)

# Start the bot
bot_token = os.environ['DISCORD_BOT_TOKEN']
if bot_token:
    client.run(bot_token, log_handler=None)
else:
    raise RuntimeError('The DISCORD_BOT_TOKEN environment variable must be set (try .env for local development)')
