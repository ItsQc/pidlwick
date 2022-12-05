# app.py
#
# The main entrypoint to the Pidlwick Discord bot for the Enter Ravenloft server.

import discord
import os
import yaml
import logging
import logging.config

import vistani_market
import tattoo_parlor

from dotenv import load_dotenv
from discord.ext import tasks

class Client(discord.Client):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.log = logging.getLogger('app.Client')

    async def setup_hook(self) -> None:
        self.task1.start()
        self.task2.start()
        self.refresh_vistani_market.start()
        self.refresh_tattoo_parlor.start()

    async def on_ready(self):
        self.log.info(f'Logged in as {self.user} (ID: {self.user.id})')
        self.log.info('------')

    # Testing Vistani Market
    @tasks.loop(seconds=5)
    async def task1(self):
        test_guild = discord.utils.get(self.guilds, name='Drury Lane')
        await vistani_market.refresh(test_guild, output_channel='bot-testing', force=True)

    @task1.before_loop
    async def before_task1(self):
        await self.wait_until_ready()

    # Testing Tattoo Parlor
    @tasks.loop(seconds=3)
    async def task2(self):
        test_guild = discord.utils.get(self.guilds, name='Drury Lane')
        await tattoo_parlor.refresh(test_guild, output_channel='bot-testing-2', force=True)

    @task2.before_loop
    async def before_task2(self):
        await self.wait_until_ready()

    # Vistani Market background task
    @tasks.loop(time=vistani_market.REFRESH_TIME)
    async def refresh_vistani_market(self):
        ravenloft_guild = discord.utils.get(self.guilds, name='Enter Ravenloft')
        await vistani_market.refresh(ravenloft_guild)

    @refresh_vistani_market.before_loop
    async def before_refresh_vistani_market(self):
        await self.wait_until_ready()

    # Tattoo Parlor background task
    @tasks.loop(time=tattoo_parlor.REFRESH_TIME)
    async def refresh_tattoo_parlor(self):
        ravenloft_guild = discord.utils.get(self.guilds, name='Enter Ravenloft')
        await tattoo_parlor.refresh(ravenloft_guild)

    @refresh_tattoo_parlor.before_loop
    async def before_refresh_tattoo_parlor(self):
        await self.wait_until_ready()

intents = discord.Intents.default()
intents.message_content = True  # For reacting to messages

client = Client(intents=intents)

# Event listeners
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

load_dotenv()  # take environment variables from .env

# Configure logging for the app and discord.py library
with open('logging.yml', 'r') as f:
    logging_config = yaml.safe_load(f)

logging.config.dictConfig(logging_config)

# Start the bot
bot_token = os.environ['DISCORD_BOT_TOKEN']
if bot_token:
    client.run(bot_token, log_handler=None)
else:
    raise RuntimeError('The DISCORD_BOT_TOKEN environment variable must be set (try .env for local development)')
