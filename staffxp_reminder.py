# staffxp_reminder.py
#
# A background task for reminding staff to claim their weekly !staffxp.

import logging

from datetime import datetime, time
from discord import Embed
from utils import embed_role_mention, random_preset_colour

log = logging.getLogger('app.staffxp_reminder')

# The Staff XP reminder is given every Saturday at 17:00 UTC.
# The remind() method is called every day and checks if it is a Saturday
TIME = time(hour=17)
WEEKDAYS = (5,)  # 0-Monday, 6-Sunday

def should_remind_today():
    """
    True iff it is a day in WEEKDAYS.
    """
    now = datetime.now()
    return now.weekday() in WEEKDAYS

async def send_reminder(channel, mention_role=None):
    """
    Post a reminder in 'channel' to claim weekly Staff XP, notifying 'mention_role' if given.
    """
    
    helpers = embed_role_mention(mention_role.id) if mention_role else '@Helper'

    text = 'Each week @Helper will receive a ping in #helper-spam to claim their weekly '
    text += 'helper xp. This is a bonus that is given to active members of staff for their '
    text += 'contributions toward helping run Enter Ravenloft. If you\'ve been active in helper '
    text += 'roles throughout the week you can use the `!staffxp` command here to claim this '
    text += 'bonus. This is mostly an honour system and we ask that if you feel/know that you '
    text += 'have not been "active" in the previous week, you do not claim it.'

    reminder = Embed(
        title='Weekly Helper XP',
        description=text,
        color=random_preset_colour(),
    )

    reminder.set_footer(text='Created by Griz ╠Octavia⁹╬Lucky⁵╬Yasmin⁶╣ • Repeats weekly')

    await channel.send(content=helpers, embed=reminder)
