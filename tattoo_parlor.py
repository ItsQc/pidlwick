# tattoo_parlor.py 
#
# Holds the logic for randomly regenerating the White Gold Hana Den's
# list of available tattoos and posting the update to OUTPUT_CHANNEL.
# 
# At present, this is just a wrapper around Quincy's tattooGenerator.py
# script which does all the heavy lifting of randomizing content and 
# formatting the output.

import discord
import logging

from datetime import datetime, time
from utils import run_script

# Run Quincy's script exactly as-is to generate the random inventory
SCRIPT_URL = 'https://raw.githubusercontent.com/ItsQc/Ravenloft-Tables/main/tattooGenerator.py'

# Post the script output to this channel when the refresh runs
OUTPUT_CHANNEL = 'helper-spam'

# The tattoo parlor refreshes at 11:00pm UTC every Sunday.
# The refresh() method is called daily and checks if it is a Sunday.
REFRESH_TIME = time(hour=23)
REFRESH_WEEKDAYS = (6,)  # 0-Monday, 6-Sunday

log = logging.getLogger('app.tattoo_parlor')

async def refresh(guild, output_channel=OUTPUT_CHANNEL, force=False):
    if not _should_refresh_today():
        if force:
            log.info('Forcing refresh on a non-scheduled day')
        else:
            log.info('Ignoring refresh on a non-scheduled day')
            return

    channel = discord.utils.get(guild.channels, name=output_channel)

    output = run_script(SCRIPT_URL)
    log.debug(output)
    
    messages = _chunk_output(output)
    for message in messages:
        await channel.send(message)

def _should_refresh_today():
    """
    True iff it is a day in REFRESH_WEEKDAYS.
    """
    now = datetime.now()
    return now.weekday() in REFRESH_WEEKDAYS

def _chunk_output(output):
    """
    Break the script output into smaller messages to stay below Discord API's 2000 character limit.
    This is brittle, relying on the exact format of tattooGenerator.py's output.
    """
    announcement_index = output.index('@Players')

    tattoos = output[:announcement_index]
    announcement = output[announcement_index:]

    return (tattoos, announcement)
