# commands.py
#
# Top-level handler for all bot commands.

import logging
import re

import vistani_market
import tattoo_parlor
import cakeday
import almanac

from datetime import datetime
from utils import embed_nickname_mention

PREFIX = '$pw '

CMD_HELLO_REGEX = re.compile(r'hello')
CMD_HELP_REGEX = re.compile(r'help|-h|--help')
CMD_REFRESH_REGEX = re.compile(r'refresh\s+(\w+)')
CMD_CAKEDAY_REGEX = re.compile(r'cakeday\s*(\d{4}-\d{2}-\d{2})?')
CMD_ALMANAC_REGEX = re.compile(r'almanac\s*(\d{4}-\d{2}-\d{2})?')

log = logging.getLogger('app.commands')

async def handle(client, message):
    """
    Parse a bot command and route it to the correct handler along with any arguments. 
    """
    cmd = message.content.removeprefix(PREFIX).strip()

    if message.author.get_role(client.staff_role.id):
        log.debug(f'Handling: "{cmd}" from {message.author.display_name}')
    else:
        log.debug(f'Ignoring command from a non-staff user: "{cmd}, {message.author.display_name}"')
        return

    if match := CMD_HELLO_REGEX.fullmatch(cmd):
        await _handle_hello(message, match)
    elif match := CMD_HELP_REGEX.fullmatch(cmd):
        await _handle_help(message, match)
    elif match := CMD_REFRESH_REGEX.fullmatch(cmd):
        await _handle_refresh(message, match)
    elif match := CMD_CAKEDAY_REGEX.fullmatch(cmd):
        await _handle_cakeday(message, match)
    elif match := CMD_ALMANAC_REGEX.fullmatch(cmd):
        await _handle_almanac(client, message, match)
    else:
        await _handle_unknown_command(message)

    # TODO: enable this once the bot has been updated with 'manage messages' permissions
    #await message.delete()

async def _handle_hello(message, _):
    await message.channel.send('*The creepy doll slowly gives you a thumbs up.*')

async def _handle_help(message, _):
    await message.channel.send('Sorry, "help" not implemented yet!')

async def _handle_refresh(message, match):
    """
    Refresh the inventory of a shop and post in the same channel as the command.
    """
    shop = match.group(1)

    match shop:
        case 'vistani':
            output = vistani_market.generate_inventory()
            await vistani_market.post_inventory(output, message.channel)
        case 'tattoo':
            output = tattoo_parlor.generate_inventory()
            await tattoo_parlor.post_inventory(output, message.channel)
        case _:
            await message.channel.send(f'Unrecognized argument to "refresh": "{shop}"')

async def _handle_cakeday(message, match):
    """
    Find the server members having their cakeday on the optional date (default 'today')
    and post them in the same channel as the command. The optional date date must be 
    given in the format YYYY-MM-DD.
    """
    cakeday_members = []
    date_words = ''

    given_date = match.group(1)
    if given_date:
        try:
            given_date = datetime.fromisoformat(given_date)
            cakeday_members = cakeday.get_members(message.guild, now=given_date)
            date_words = f'on {match.group(1)} (UTC)'
        except ValueError:
            await message.channel.send(f'Invalid date: "{given_date}" (must be YYYY-MM-DD)')
            return
    else:
        cakeday_members = cakeday.get_members(message.guild)
        date_words = 'today'

    if cakeday_members:
        member_words = 'member has' if len(cakeday_members) == 1 else 'members have'
        output = f'**{len(cakeday_members)} {member_words} their cakeday {date_words}:**\n'
        for member, years in cakeday_members:
            output += f'\t* {embed_nickname_mention(member.id)} - {years} year'
            if years > 1:
                output += 's'
            output += '\n'
        await message.channel.send(output)
    else:
        await message.channel.send(f'No members have their cakeday {date_words}.')

async def _handle_almanac(client, message, match):
    """
    Lookup the entry for the given date in the Barovian Almanac and display it as a
    Discord Embed. The date defaults to today but can also be given in YYYY-MM-DD format.
    """
    given_date = match.group(1)
    if given_date:
        try:
            given_date = datetime.fromisoformat(given_date)
            generated = almanac.generate_embed(client.almanac_gsheet_id, timestamp=given_date)
        except ValueError:
            await message.channel.send(f'Invalid date: "{given_date}" (must be YYYY-MM-DD)')
            return
    else:
        generated = almanac.generate_embed(client.almanac_gsheet_id)

    await almanac.post_entry(generated, message.channel)

async def _handle_unknown_command(message):
    command = message.content.removeprefix(PREFIX)
    await message.channel.send(f'Unrecognized command: "{command}"')
