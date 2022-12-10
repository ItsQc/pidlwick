# utils.py
#
# Misc utilities for the Pidlwick bot.

import urllib.request

from io import StringIO
from contextlib import redirect_stdout

# TODO: Make this async
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
