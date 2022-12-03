import discord
import urllib.request
import os

from io import StringIO
from contextlib import redirect_stdout
from dotenv import load_dotenv

# For now we run Quincy's scripts exactly as-is to randomly generate the item tables. 
SCRIPT_URLS = {
    'Vistani Market': 'https://raw.githubusercontent.com/ItsQc/Ravenloft-Tables/main/marketGenerator.py',
    'Tattoo Parlor': 'https://raw.githubusercontent.com/ItsQc/Ravenloft-Tables/main/tattooGenerator.py'
}

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

    if message.content.startswith('$refresh vistani'):
        output = run_script(SCRIPT_URLS['Vistani Market'])

        # Break the output into 4 separate messages to stay under Discord API's 2000 character limit.
        scroll_index = output.index('**Spell Scrolls**')
        materials_index = output.index('**Special Materials**')
        announcement_index = output.index('@Players')

        item_output = output[:scroll_index]
        scroll_output = output[scroll_index:materials_index]
        material_output = output[materials_index:announcement_index]
        announcement_output = output[announcement_index:]

        print(output)
        await message.channel.send(item_output)
        await message.channel.send(scroll_output)
        await message.channel.send(material_output)
        await message.channel.send(announcement_output)

    if message.content.startswith('$refresh tattoo'):
        output = run_script(SCRIPT_URLS['Tattoo Parlor'])
        
        print(output)
        await message.channel.send(output)

def run_script(script_url):
    f = urllib.request.urlopen(script_url)
    script = f.read()

    s = StringIO()
    with redirect_stdout(s):
        exec(script, globals())
    output = s.getvalue()

    return output

load_dotenv()  # take environment variables from .env

bot_token = os.environ['DISCORD_BOT_TOKEN']
if bot_token:
    client.run(bot_token)
else:
    raise RuntimeError('The DISCORD_BOT_TOKEN environment variable must be set (try .env for local development)')
