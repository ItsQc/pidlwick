# cakeday.py 
#
# Holds the logic for finding users with a given Cakeday (AKA anniversary of them joining the server)
# and congratulating them with a special announcement.

import logging

from datetime import date, time

# The Cakeday Announcement task checks every day at 8pm UTC
CHECK_TIME = time(hour=20)

log = logging.getLogger('app.cakeday')

def get_members(guild, today=date.today()):
    """
    Get a list of all server members having their cakeday 'today' as tuples
    of (member, years). The list is sorted by years ASC primary, name ASC secondary.
    """
    cakeday_members = []
    
    for member in guild.members:
        joined_at = member.joined_at
        if joined_at.month == today.month and joined_at.day == today.day and joined_at.year < today.year:
            log.debug(f'Server {guild.name} member ({member.name}, {member.joined_at}) has their cakeday on {today}')
            years = today.year - joined_at.year
            cakeday_members.append((member, years))

    cakeday_members.sort(key=lambda x: x[0]) # secondary sort by name ASC
    cakeday_members.sort(key=lambda x: x[1]) # primary sort by years ASC

    return cakeday_members

def make_announcement(members, channel):
    """
    Make a public announcement to the playerbase congratulating cakeday members.
    """
    # Announcement template text
    # Insert user mentions for cakeday players
    # Cake image attachment
    pass

def notify_staff(members, channel):
    """
    Make a private announcement so that staff can add a special role to cakeday members.
    """
    # Announcement template text
    # List of cakeday players
    # Mention to Mods
    pass
