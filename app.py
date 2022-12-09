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
import cakeday

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

        self.players_role_name = os.environ['PLAYERS_ROLE']
        self.vistani_channel_name = os.environ['VISTANI_MARKET_CHANNEL']
        self.tattoo_channel_name = os.environ['TATTOO_PARLOR_CHANNEL']
        self.cakeday_public_channel_name = os.environ['CAKEDAY_PUBLIC_CHANNEL']
        self.cakeday_private_channel_name = os.environ['CAKEDAY_PRIVATE_CHANNEL']

    async def setup_hook(self) -> None:
        self.refresh_vistani_market.start()
        self.refresh_tattoo_parlor.start()

    async def on_ready(self):
        self.log.info(f'Logged in as {self.user} (ID: {self.user.id})')
        self.log.info('------')

    # Vistani Market background task
    @tasks.loop(time=vistani_market.REFRESH_TIME)
    async def refresh_vistani_market(self):
        # This could be done better, likely by spawning a separate thread or task for each guild.
        # But for our tiny scale and number of servers (2-5) this is probably ok.
        for guild in self.guilds:
            channel = discord.utils.get(guild.channels, name=self.vistani_channel_name)
            if not channel:
                self.log.error(f'Unable to find channel {self.vistani_channel_name} in server {guild.name}')
                return

            role = discord.utils.get(guild.roles, name=self.players_role_name)
            if not role:
                self.log.error(f'Unable to find role {self.players_role_name} in server {guild.name}: @mention will not work')

            if vistani_market.should_refresh_today():
                self.log.info(f'Refreshing Vistani Market in {guild.name} - {channel.name}')
                output = vistani_market.generate_inventory()
                await vistani_market.post_inventory(output, channel, role)
            else:
                self.log.debug(f'Not refreshing Vistani Market for {guild.name} - {channel.name} as it is not a scheduled day')


    @refresh_vistani_market.before_loop
    async def before_refresh_vistani_market(self):
        await self.wait_until_ready()

    # Tattoo Parlor background task
    @tasks.loop(time=tattoo_parlor.REFRESH_TIME)
    async def refresh_tattoo_parlor(self):
        for guild in self.guilds:
            channel = discord.utils.get(guild.channels, name=self.tattoo_channel_name)
            if not channel:
                self.log.error(f'Unable to find channel {self.tattoo_channel_name} in server {guild.name}')
                return

            role = discord.utils.get(guild.roles, name=self.players_role_name)
            if not role:
                self.log.error(f'Unable to find role {self.players_role_name} in server {guild.name}: @mention will not work')    

            if tattoo_parlor.should_refresh_today():
                self.log.info(f'Refreshing Tattoo Parlor in {guild.name} - {channel.name}')
                output = tattoo_parlor.generate_inventory()
                await tattoo_parlor.post_inventory(output, channel, role)
            else:
                self.log.debug(f'Not refreshing Tattoo Parlor for {guild.name} - {channel.name} as it is not a scheduled day')

    @refresh_tattoo_parlor.before_loop
    async def before_refresh_tattoo_parlor(self):
        await self.wait_until_ready()

    # Cakeday Announcement background task
    @tasks.loop(time=cakeday.CHECK_TIME)
    async def announce_cakedays(self):
        for guild in self.guilds:
            public_channel = discord.utils.get(guild.channels, name=self.cakeday_public_channel_name)
            private_channel = discord.utils.get(guild.channels, name=self.cakeday_private_channel_name)

            if not public_channel:
                self.log.error(f'Unable to find channel {self.cakeday_public_channel_name} in server {guild.name}')
                return

            members = cakeday.get_members(guild)
            if members:
                self.log.info(f'Server {guild.name} has {len(members)} members with cakedays today')
                cakeday.announce_public(members, public_channel)

                if private_channel:
                    cakeday.announce_private(members, private_channel)
                else:
                    self.log.error(f'Unable to find channel {self.cakeday_private_channel_name} in server {guild.name}')
            else:
                self.log.info(f'Server {guild.name} has no members with cakedays today')

    @announce_cakedays.before_loop
    async def before_announce_cakedays(self):
        await self.wait_until_ready()

intents = discord.Intents.default()
intents.message_content = True  # For reacting to messages
intents.members = True  # For iterating over guild.members
client = Client(intents=intents)

# Event listeners - route bot commands to the 'command' module
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
