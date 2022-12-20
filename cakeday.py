# cakeday.py 
#
# Holds the logic for finding users with a given Cakeday (AKA anniversary of them joining the server)
# and congratulating them with a special announcement.

import logging

from discord import File
from datetime import datetime, time, timezone
from utils import embed_role_mention, embed_nickname_mention, partition

# The Cakeday Announcement task checks every day at 8pm UTC
CHECK_TIME = time(hour=20)

# Relative path to the image for the public announcement
IMAGE_PATH = 'images/cake.png'

log = logging.getLogger('app.cakeday')

def get_members(guild, now=datetime.now(timezone.utc)):
    """
    Get a list of all server members having their cakeday on the same date as 'now' as tuples
    of (member, years). The list is sorted by years ASC primary, name ASC secondary.
    """
    cakeday_members = []

    for member in guild.members:
        if member.bot:
            continue # Cake is for humans

        joined_at = member.joined_at
        if joined_at.month == now.month and joined_at.day == now.day and joined_at.year < now.year:
            log.debug(f'Server {guild.name} member ({member.display_name}, {member.joined_at}) has their cakeday on {now.date()}')
            years = now.year - joined_at.year
            cakeday_members.append((member, years))

    cakeday_members.sort(key=lambda x: x[0].display_name) # secondary sort by name ASC
    cakeday_members.sort(key=lambda x: x[1]) # primary sort by years ASC

    return cakeday_members

async def make_announcement(members, channel):
    """
    Make a public announcement to the playerbase congratulating cakeday members.
    """
    if not members:
        log.warn('make_announcement called with no members - likely a bug')
        return

    preface = '**A most fortuitous day!**\n'
    preface += '\n'
    preface += '```The mists swirl and whip around the feet of various adventurers who are going '
    preface += 'about their day across the lands, their fevered excitement an unspoken recognition '
    preface += 'of your commitment and fortitude against all odds in the dark and desolate lands '
    preface += 'of Barovia. From somewhere beyond the veil you feel a sense of warmth and calm, '
    preface += 'a spiritual embrace that talks without speaking...```'
    preface += '\n'
    preface += 'Congratulations! Today marks a momentous milestone!\n'
    preface += '\n'

    callouts = []
    for member, years in members:
        callout = f'{embed_nickname_mention(member.id)}'
        callout += f' - You have been a part of our humble community for {years} '
        callout += 'year!\n' if years == 1 else 'years!\n'
        callouts.append(callout)

    thanks = 'From the staff, and the rest of the players here, thank you for being a part of '
    thanks += 'our digital grimdark home and we look forward to celebrating again next year!\n'
    thanks += '\n'
    thanks += '**Happy Cake Day!**\n'

    epilogue = '*Players who achieve anniversaries in Enter Ravenloft will be recognised for '
    epilogue += 'their commitment to the server with a special ⭐ (optional) alongside their name.*'

    if len(callouts) <= 10:
        return await _announce_compact(channel, preface, callouts, thanks, epilogue)
    else:
        return await _announce_split(channel, preface, callouts, thanks, epilogue)

async def _announce_compact(channel, preface, callouts, thanks, epilogue):
    """
    Make the public announcement in a single message (+ epilogue). Return the
    primary message that was sent.
    """
    output = preface
    for callout in callouts:
        output += callout
    output += '\n'
    output += thanks

    image = None
    with open(IMAGE_PATH, 'rb') as f:
        image = File(f)

    sent = await channel.send(content=output, file=image)

    # The epilogue text is sent as a separate message so that the image attachment appears
    # visually just below "Happy Cake Day".
    await channel.send(epilogue)

    return sent

async def _announce_split(channel, preface, callouts, thanks, epilogue):
    """
    Make the public announcement by splitting member mentions into multiple messages.
    This is to stay below Discord's 2000 character limit for large numbers of members.
    Returns the first "preface" message that was sent.
    """
    sent = await channel.send(preface)

    for batch in partition(callouts, 10):
        await channel.send(batch.join(''))

    image = None
    with open(IMAGE_PATH, 'rb') as f:
        image = File(f)

    await channel.send(content=thanks, file=image)

    await channel.send(epilogue)

    return sent

async def add_role(members, year_one_player_role):
    """
    Adds the Year 1 Player role to the specified members.
    """
    if year_one_player_role:
        for member, years in members:
            await member.add_roles(year_one_player_role, reason='Cakeday')
        return True
    else:
        log.error(f'year_one_player_role is None, cannot add role to {len(members)} members')
        return False

async def notify_staff(members, channel, role, message_url, success):
    """
    Make a private announcement so that staff can add a special role to cakeday members.
    """
    if not members:
        log.warn('notify_staff called with no members - likely a bug')
        return

    log.info(f'Notifying mods about {len(members)} members having cakedays today')

    mods = embed_role_mention(role.id) if role and not success else 'Mods'
    member_words = 'member is' if len(members) == 1 else 'members are'
    output = f'{mods} - {len(members)} {member_words} celebrating their cakeday today ({message_url}):\n'

    for member, years in members:
        output += f'\t{member.display_name} ({years} '
        output += 'years)\n' if years > 1 else 'year)\n' 

    if success:
        output += 'The `Year 1 Player` role was added automatically - nothing for you to do!\n'
        output += '...*UNLESS* one of these users was a Staff member. Then you\'ll need to add the '
        output += 'appropriate additional role(s) yourself (Year 1 Helper, etc).'
    else:
        output += 'The `Year 1 Player` role was **NOT** added automatically - please add it when you can.'

    await channel.send(output)
