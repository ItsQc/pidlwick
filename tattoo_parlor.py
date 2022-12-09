# tattoo_parlor.py 
#
# Holds the logic for randomly regenerating the White Gold Hana Den's
# list of available tattoos and posting the update to OUTPUT_CHANNEL.
# 
# At present, this is just a wrapper around Quincy's tattooGenerator.py
# script which does all the heavy lifting of randomizing content and 
# formatting the output.

import logging

from datetime import datetime, time
from utils import run_script, embed_role_mention

# Run Quincy's script exactly as-is to generate the random inventory
SCRIPT_URL = 'https://raw.githubusercontent.com/ItsQc/Ravenloft-Tables/main/tattooGenerator.py'

# The tattoo parlor refreshes at midnight UTC every Sunday.
# The refresh() method is called daily and checks if it is a Sunday.
REFRESH_TIME = time()
REFRESH_WEEKDAYS = (6,)  # 0-Monday, 6-Sunday

log = logging.getLogger('app.tattoo_parlor')

def should_refresh_today():
    """
    True iff it is a day in REFRESH_WEEKDAYS.
    """
    now = datetime.now()
    return now.weekday() in REFRESH_WEEKDAYS

def generate_inventory():
    """
    Run Quincy's script to generate the randomized inventory.
    """
    output = run_script(SCRIPT_URL)
    log.debug(output)
    return output

async def post_inventory(inventory, channel, mention_role=None):
    """
    Post the content of 'inventory' to 'channel', breaking it into smaller fragments.
    """
    messages = _chunk_output(inventory, mention_role)
    for message in messages:
        await channel.send(message)

def _chunk_output(output, mention_role):
    """
    Break the script output into smaller messages to stay below Discord API's 2000 character limit.
    This is brittle, relying on the exact format of tattooGenerator.py's output.
    """
    announcement_index = output.index('@Players')

    tattoos = output[:announcement_index]
    announcement = output[announcement_index:]

    if mention_role:
        announcement = announcement.replace('@Players', embed_role_mention(mention_role.id))

    return (tattoos, announcement)
