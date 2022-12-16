# almanac.py
#
# Holds the logic for generating Barovian Alamanac entries for a given date as Discord embeds,
# including information on weather, moon phase, calendar, etc.

import logging

from datetime import datetime, timezone, time
from discord import Embed
from utils import random_preset_colour, load_google_sheet

log = logging.getLogger('app.almanac')

# The Almanac reading is posted daily at midnight UTC.
REFRESH_TIME = time()

# CSV field names, taken verbatim from the Google Sheet header cells
DAY_OF_YEAR = 'Real World Day of year'
DATE = 'Real World\n Date'
SPECIAL = 'Special\n(special note about this day)'
BAROVIAN_MONTH = 'Barovian Month'
BAROVIAN_DAY = 'Barovian Day'
MOON_PHASE = 'Moon Phase'
SEASON = 'Season'
TEMPERATURE = ':thermometer:\nTemperature (High / Low)'
WIND = ':wind_blowing_face: Wind'
PRECIPITATION = ':droplet: Precipitation'
SUNRISE = ':sunrise_over_mountains: Sunrise'
SUNSET = ':sunrise_over_mountains: Sunset '

def generate_embed(sheet_id, timestamp=datetime.now(timezone.utc)):
    """
    Lookup alamanac data and return an Embed for the given date.
    """
    entry = _fetch_data(sheet_id, timestamp)

    embed = Embed(
        title=':calendar_spiral: Barovian Almanac',
        description='Daily forecast for the Town of Vallaki. Higher elevations are cooler and more likely to have snow.',
        color=random_preset_colour(),
    )

    # Hack: The Discord API requires a non-empty value for embed fields, but this won't be rendered.
    # Used to control whitespace around the "section headers" for Almanac, Weather, and Special Note.
    NULL_VALUE = '** **'

    barovian_year = f'{timestamp.year - 1286} BC'  # years since Strahd became a :vampire:

    embed.add_field(name='Day', value=entry[BAROVIAN_DAY], inline=True)
    embed.add_field(name='Month', value=entry[BAROVIAN_MONTH], inline=True)
    embed.add_field(name='Year', value=barovian_year, inline=True)

    embed.add_field(name=f'{NULL_VALUE}\n**__Almanac__**', value=NULL_VALUE, inline=False)

    embed.add_field(name=':sunrise_over_mountains: Sunrise', value=entry[SUNRISE], inline=True)
    embed.add_field(name=':sunrise_over_mountains: Sunset', value=entry[SUNSET], inline=True)
    embed.add_field(name='Moon Phase', value=entry[MOON_PHASE], inline=True)

    embed.add_field(name=f'{NULL_VALUE}\n**__Weather__**', value=NULL_VALUE, inline=False)

    embed.add_field(name=':thermometer: Temperature', value=entry[TEMPERATURE], inline=True)
    embed.add_field(name=':wind_blowing_face: Wind Speed', value=entry[WIND], inline=True)
    embed.add_field(name=':droplet: Precipitation', value=entry[PRECIPITATION], inline=True)
    embed.add_field(name='Season', value=entry[SEASON], inline=True)

    special = entry[SPECIAL]
    if special:
        embed.add_field(name=f'{NULL_VALUE}\n{special}', value=NULL_VALUE, inline=False)
    else:
         embed.add_field(name=NULL_VALUE, value=NULL_VALUE, inline=False)

    embed.set_footer(text='Remember, DMs can override temperature or date to suit their events.\n' + 
        'Based on u/Silphaen and others in r/CurseofStrahd for calendar and weather generators.')

    return embed

async def post_entry(entry, channel):
    """
    Send a message consisting of the Embed entry to the specified channel.
    Return the message that was sent.
    """
    return await channel.send(embed=entry)

# TODO: Make this async
def _fetch_data(sheet_id, timestamp):
    """
    Read the almanac data from the Google Spreadsheet and return the entry for the given date as a dictionary.
    """
    almanac_data = load_google_sheet(sheet_id)
    log.info(f'Retrieved {len(almanac_data)} entries of almanac data from Google Sheets')

    formatted_date = timestamp.strftime('%d-%b').lstrip('0')  # e.g. 7-Jan

    for datum in almanac_data:
        if datum[DATE] == formatted_date:
            log.info(f'Found almanac entry for {formatted_date}: {datum}')
            return datum

    log.error(f'Did not find almanac entry for {formatted_date} in Google Sheet data')
    return None
