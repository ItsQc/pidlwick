# vistani_market.py 
#
# Holds the logic for randomly regenerating the Vistani Market inventory
# and posting the update to OUTPUT_CHANNEL.
# 
# At present, this is just a wrapper around Quincy's marketGenerator.py
# script which does all the heavy lifting of randomizing content and 
# formatting the output.

import discord
import logging

from datetime import date, time
from utils import run_script

# Run Quincy's script exactly as-is to generate the random inventory
SCRIPT_URL = 'https://raw.githubusercontent.com/ItsQc/Ravenloft-Tables/main/marketGenerator.py'

# Post the script output to this channel when the refresh runs
OUTPUT_CHANNEL = 'helper-spam'

# The Vistani Market refreshes at 11:00pm UTC every 3 days.
# The refresh() method is called daily and checks if it has been a multiple
# of 3 days since an authoritative start date ("epoch").
REFRESH_TIME = time(hour=23)
REFRESH_EPOCH = date(2022, 12, 2)
REFRESH_INTERVAL_DAYS = 3

log = logging.getLogger('app.vistani_market')

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
    True iff it has been a multiple of REFRESH_INTERVAL_DAYS since REFRESH_EPOCH.
    """
    today = date.today()
    delta = today - REFRESH_EPOCH
    return delta.days % REFRESH_INTERVAL_DAYS == 0

def _chunk_output(output):
    """
    Break the script output into smaller messages to stay below Discord API's 2000 character limit.
    This is brittle, relying on the exact format of marketGenerator.py's output.
    """
    scroll_index = output.index('**Spell Scrolls**')
    materials_index = output.index('**Special Materials**')
    announcement_index = output.index('@Players')

    items = output[:scroll_index]
    scrolls = output[scroll_index:materials_index]
    materials = output[materials_index:announcement_index]
    announcement = output[announcement_index:]

    return (items, scrolls, materials, announcement)
