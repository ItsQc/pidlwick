# client.py
#
# This module holds the code for the Client class, which our connection to the Discord API.
# Code in this class is responsible for looking up server entities and bootstrapping any
# background tasks.

import discord
import logging
import os

import cakeday
import commands
import tattoo_parlor
import vistani_market

from discord.ext import tasks

class Client(discord.Client):
    """
    The Client class leverages the Discord APIs to connect the bot to Discord.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.log = logging.getLogger('app.Client')

    async def setup_hook(self) -> None:
        self.refresh_vistani_market.start()
        self.refresh_tattoo_parlor.start()
        self.announce_cakedays.start()

    async def on_ready(self):
        self.log.info(f'Logged in as {self.user} (ID: {self.user.id})')
        self.log.info('------')

        log_result = lambda x, subject: self.log.info(f'Found {subject} = {x.name}') if x else self.log.error(f'Unable to find {subject}')

        self.guild = self.get_guild(int(os.environ['SERVER']))
        log_result(self.guild, 'server')
    
        self.maintainer = self.guild.get_member(int(os.environ['MAINTAINER']))
        log_result(self.maintainer, 'maintainer')

        self.vistani_inventory_channel = self.guild.get_channel(int(os.environ['VISTANI_INVENTORY_CHANNEL']))
        log_result(self.vistani_inventory_channel, 'Vistani Market inventory channel')

        self.tattoo_inventory_channel = self.guild.get_channel(int(os.environ['VISTANI_INVENTORY_CHANNEL']))
        log_result(self.tattoo_inventory_channel, 'Tattoo Parlor inventory channel')

        self.cakeday_announcement_channel = self.guild.get_channel(int(os.environ['CAKEDAY_ANNOUNCEMENT_CHANNEL']))
        log_result(self.cakeday_announcement_channel, 'cakeday announcement channel')

        self.bot_notification_channel = self.guild.get_channel(int(os.environ['BOT_NOTIFICATION_CHANNEL']))
        log_result(self.bot_notification_channel, 'bot notification channel')

        self.bot_development_channel = self.guild.get_channel(int(os.environ['BOT_DEVELOPMENT_CHANNEL']))
        log_result(self.bot_development_channel, 'bot development channel')

        self.players_role = self.guild.get_role(int(os.environ['PLAYERS_ROLE']))
        log_result(self.players_role, 'Players role')

        self.staff_role = self.guild.get_role(int(os.environ['STAFF_ROLE']))
        log_result(self.staff_role, 'Staff role')

        self.mods_role = self.guild.get_role(int(os.environ['MODS_ROLE']))
        log_result(self.mods_role, 'Mods role')

    # Message handling: route bot commands to the commands module
    async def on_message(self, message):
        if message.author == self.user:
            return
        elif message.content.startswith(commands.PREFIX):
            await commands.handle(self, message)

    # Vistani Market background task
    @tasks.loop(time=vistani_market.REFRESH_TIME)
    async def refresh_vistani_market(self):
        if vistani_market.should_refresh_today():
            self.log.info(f'Refreshing Vistani Market inventory in {self.vistani_inventory_channel.name}')
            output = vistani_market.generate_inventory()
            await vistani_market.post_inventory(output, self.vistani_inventory_channel, self.players_role)
        else:
            self.log.info(f'Not refreshing Vistani Market inventory for {self.vistani_inventory_channel.name} as it is not a scheduled day')

    @refresh_vistani_market.before_loop
    async def before_refresh_vistani_market(self):
        await self.wait_until_ready()

    # Tattoo Parlor background task
    @tasks.loop(time=tattoo_parlor.REFRESH_TIME)
    async def refresh_tattoo_parlor(self):
        if tattoo_parlor.should_refresh_today():
            self.log.info(f'Refreshing Tattoo Parlor inventory in {self.tattoo_inventory_channel.name}')
            output = tattoo_parlor.generate_inventory()
            await tattoo_parlor.post_inventory(output, self.tattoo_inventory_channel, self.players_role)
        else:
            self.log.info(f'Not refreshing Tattoo Parlor inventory for {self.tattoo_inventory_channel} as it is not a scheduled day')

    @refresh_tattoo_parlor.before_loop
    async def before_refresh_tattoo_parlor(self):
        await self.wait_until_ready()

    # Cakeday Announcement background task
    @tasks.loop(time=cakeday.CHECK_TIME)
    async def announce_cakedays(self):
        members = cakeday.get_members(self.guild)
        if members:
            self.log.info(f'Server {self.guild.name} has {len(members)} members with cakedays today!')
            await cakeday.make_announcement(members, self.cakeday_announcement_channel)
            await cakeday.notify_staff(members, self.bot_notification_channel, self.mods_role)
        else:
            self.log.info(f'Server {self.guild.name} has no members with cakedays today')

    @announce_cakedays.before_loop
    async def before_announce_cakedays(self):
        await self.wait_until_ready()
