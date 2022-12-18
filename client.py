# client.py
#
# This module holds the code for the Client class, which our connection to the Discord API.
# Code in this class is responsible for looking up server entities and bootstrapping any
# background tasks.

import discord
import logging
import os

import almanac
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
        self.refresh_almanac.start()
        self.heartbeat.start()

    async def on_ready(self):
        self.log.info(f'Logged in as {self.user} (ID: {self.user.id})')
        self.log.info('------')

        log_result = lambda x, subject: self.log.info(f'Found {subject} = {x.name}') if x else self.log.error(f'Unable to find {subject}')
        log_nameless = lambda x, subject: self.log.info(f'Found {subject} = {x}') if x else self.log.error(f'Unable to find {subject}')

        self.guild = self.get_guild(int(os.environ['SERVER']))
        log_result(self.guild, 'server')
    
        self.maintainer = self.guild.get_member(int(os.environ['MAINTAINER']))
        log_result(self.maintainer, 'maintainer')

        # Channels
        self.vistani_inventory_channel = self.guild.get_channel(int(os.environ['VISTANI_INVENTORY_CHANNEL']))
        log_result(self.vistani_inventory_channel, 'Vistani Market inventory channel')

        self.tattoo_inventory_channel = self.guild.get_channel(int(os.environ['VISTANI_INVENTORY_CHANNEL']))
        log_result(self.tattoo_inventory_channel, 'Tattoo Parlor inventory channel')

        self.cakeday_announcement_channel = self.guild.get_channel(int(os.environ['CAKEDAY_ANNOUNCEMENT_CHANNEL']))
        log_result(self.cakeday_announcement_channel, 'cakeday announcement channel')

        self.almanac_channel = self.guild.get_channel(int(os.environ['ALMANAC_CHANNEL']))
        log_result(self.almanac_channel, 'Barovian Almanac channel')

        self.bot_notification_channel = self.guild.get_channel(int(os.environ['BOT_NOTIFICATION_CHANNEL']))
        log_result(self.bot_notification_channel, 'bot notification channel')

        self.bot_development_channel = self.guild.get_channel(int(os.environ['BOT_DEVELOPMENT_CHANNEL']))
        log_result(self.bot_development_channel, 'bot development channel')

        # Roles
        self.players_role = self.guild.get_role(int(os.environ['PLAYERS_ROLE']))
        log_result(self.players_role, 'Players role')

        self.staff_role = self.guild.get_role(int(os.environ['STAFF_ROLE']))
        log_result(self.staff_role, 'Staff role')

        self.mods_role = self.guild.get_role(int(os.environ['MODS_ROLE']))
        log_result(self.mods_role, 'Mods role')

        self.year_one_player_role = self.guild.get_role(int(os.environ['YEAR_ONE_PLAYER_ROLE']))
        log_result(self.year_one_player_role, 'Year 1 Player role')

        # Google Sheets
        self.almanac_gsheet_id = os.environ['ALMANAC_GSHEET_ID']
        log_nameless(self.almanac_gsheet_id, 'Almanac Google Sheet ID')

    # Message handling: route bot commands to the commands module
    async def on_message(self, message):
        if message.author == self.user:
            return
        elif message.content.startswith(commands.PREFIX):
            await commands.handle(self, message)

    # Vistani Market background task
    @tasks.loop(time=vistani_market.REFRESH_TIME)
    async def refresh_vistani_market(self):
        self.log.debug('refresh_vistani_market: scheduled task has started')

        if vistani_market.should_refresh_today():
            self.log.info(f'Refreshing Vistani Market inventory in {self.vistani_inventory_channel.name}')
            output = vistani_market.generate_inventory()
            await vistani_market.post_inventory(output, self.vistani_inventory_channel, self.players_role)
        else:
            self.log.info(f'Not refreshing Vistani Market inventory for {self.vistani_inventory_channel.name} as it is not a scheduled day')

    @refresh_vistani_market.before_loop
    async def before_refresh_vistani_market(self):
        self.log.debug('before_refresh_vistani_market: waiting for readiness')
        await self.wait_until_ready()
        self.log.debug('before_refresh_vistani_market: ready now')

    # Tattoo Parlor background task
    @tasks.loop(time=tattoo_parlor.REFRESH_TIME)
    async def refresh_tattoo_parlor(self):
        self.log.debug('refresh_tattoo_parlor: scheduled task has started')

        if tattoo_parlor.should_refresh_today():
            self.log.info(f'Refreshing Tattoo Parlor inventory in {self.tattoo_inventory_channel.name}')
            output = tattoo_parlor.generate_inventory()
            await tattoo_parlor.post_inventory(output, self.tattoo_inventory_channel, self.players_role)
        else:
            self.log.info(f'Not refreshing Tattoo Parlor inventory for {self.tattoo_inventory_channel} as it is not a scheduled day')

    @refresh_tattoo_parlor.before_loop
    async def before_refresh_tattoo_parlor(self):
        self.log.debug('before_refresh_tattoo_parlor: waiting for readiness')
        await self.wait_until_ready()
        self.log.debug('before_refresh_tattoo_parlor: ready now')

    # Cakeday Announcement background task
    @tasks.loop(time=cakeday.CHECK_TIME)
    async def announce_cakedays(self):
        self.log.debug('announce_cakedays: scheduled task has started')

        members = cakeday.get_members(self.guild)
        if members:
            self.log.info(f'Server {self.guild.name} has {len(members)} members with cakedays today!')
            message = await cakeday.make_announcement(members, self.cakeday_announcement_channel)

            try:
                add_role_success = cakeday.add_role(members, self.year_one_player_role)
            except discord.Forbidden | discord.HTTPException as e:
                self.log.error(f'Exception while adding Year 1 Player role: {e}')
                add_role_success = False
            finally:
                await cakeday.notify_staff(members, self.bot_notification_channel, self.mods_role, message.jump_url, add_role_success)
        else:
            self.log.info(f'Server {self.guild.name} has no members with cakedays today')

    @announce_cakedays.before_loop
    async def before_announce_cakedays(self):
        self.log.debug('before_announce_cakedays: waiting for readiness')
        await self.wait_until_ready()
        self.log.debug('before_announce_cakedays: ready now')

    # Barovian Almanac background task
    @tasks.loop(time=almanac.REFRESH_TIME)
    async def refresh_almanac(self):
        self.log.debug('refresh_almanac: scheduled task has started')

        entry = almanac.generate_embed(self.almanac_gsheet_id)
        await almanac.post_entry(entry, self.almanac_channel)

    @refresh_almanac.before_loop
    async def before_refresh_almanac(self):
        self.log.debug('before_refresh_almanac: waiting for readiness')
        await self.wait_until_ready()
        self.log.debug('before_refresh_almanac: ready now')

    # Heartbeat background task
    @tasks.loop(hours=1)
    async def heartbeat(self):
        self.log.debug('Heartbeat')

    @heartbeat.before_loop
    async def before_heartbeat(self):
        await self.wait_until_ready()
