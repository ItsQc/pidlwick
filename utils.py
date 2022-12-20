# utils.py
#
# Misc utilities for the Pidlwick bot.

import urllib.request
import random
import csv

from io import StringIO
from contextlib import redirect_stdout
from discord import Colour
from traceback import format_exception

# TODO: Make this async (or ideally remove it after porting shop scripts into Pidlwick)
def run_script(script_url):
    """
    Retrieves content from `script_url` and runs it as a Python script using `exec`, returning
    the stdout output. Brittle? Yes. Unsafe? Oh yeah. Temporary hack only, to be removed once
    the content generation logic is brought into Pidlwick.
    """
    f = urllib.request.urlopen(script_url)
    script_content = f.read()

    s = StringIO()
    with redirect_stdout(s):
        exec(script_content, globals())
    script_stdout = s.getvalue()

    return script_stdout

def partition(l, n):
    """
    Partition the list l into chunks/sublists of size n.
    """
    for i in range(0, len(l), n):
        yield l[i:i + n]

def embed_role_mention(role_id):
    """
    Returns an embedding suitable for a role mention, e.g. '@Players'.
    """
    return f'<@&{role_id}>'

def embed_nickname_mention(user_id):
    """
    Returns an embedding of a mention using a server-specific nickname.
    """
    return f'<@!{user_id}>'

def random_preset_colour(choices=None):
    """
    Returns a random Colour from the passed-in iterable, or from Discord.py's built-in selection.
    """
    if not choices:
        choices = (
            Colour.blue(),
            Colour.blurple(),
            Colour.brand_green(),
            Colour.brand_red(),
            Colour.dark_blue(),
            Colour.dark_gold(),
            Colour.dark_green(),
            Colour.dark_grey(),
            Colour.dark_magenta(),
            Colour.dark_orange(),
            Colour.dark_purple(),
            Colour.dark_red(),
            Colour.dark_teal(),
            Colour.dark_theme(),
            Colour.darker_grey(),
            Colour.gold(),
            Colour.green(),
            Colour.greyple(),
            Colour.light_grey(),
            Colour.lighter_grey(),
            Colour.magenta(),
            Colour.og_blurple(),
            Colour.orange(),
            Colour.purple(),
            Colour.red(),
            Colour.teal(),
            Colour.yellow(),
        )

    return random.choice(choices)

def random_colour():
    """
    Returns a Colour having completely random hue.
    """
    return Colour.random()

def load_google_sheet(sheet_id):
    """
    Loads a Google Spreadsheet formatted as a list of dictionaries.
    This looks at only the first sheet if there are multiple and interprets the first row as a header
    with field names for all of the subsequent rows.
    """
    url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv'

    response = urllib.request.urlopen(url)
    csv_data = response.read().decode(response.headers.get_content_charset())
    s = StringIO(csv_data, newline='')

    reader = csv.DictReader(s)
    entries = []
    for entry in reader:
        entries.append(entry)

    return entries

async def notify_maintainer(channel, user, error):
    """
    Attempts to @mention a user in the given channel to inform them of an error.
    """
    if not channel:
        return  # (shrug)

    maintainer = embed_nickname_mention(user.id) if user else 'Boss'

    msg = f'Uh-oh, something went wrong. Hey {maintainer}, take a look at this:\n'
    msg += '```\n'
    msg += ''.join(format_exception(error)) if isinstance(error, Exception) else f'{error}\n'
    msg += '```'

    await channel.send(msg)
