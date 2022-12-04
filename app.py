import discord
import urllib.request
import os

from io import StringIO
from contextlib import redirect_stdout
from dotenv import load_dotenv
from discord.ext import tasks

# For now we run Quincy's scripts exactly as-is to randomly generate the item tables. 
SCRIPT_URLS = {
    'Vistani Market': 'https://raw.githubusercontent.com/ItsQc/Ravenloft-Tables/main/marketGenerator.py',
    'Tattoo Parlor': 'https://raw.githubusercontent.com/ItsQc/Ravenloft-Tables/main/tattooGenerator.py'
}

intents = discord.Intents.default()
intents.message_content = True

class MyClient(discord.Client):

    async def setup_hook(self) -> None:
        self.task1.start()
        self.task2.start()

    @tasks.loop(seconds=5)
    async def task1(self):
        guild = discord.utils.get(self.guilds, name='Drury Lane')
        channel1 = discord.utils.get(guild.channels, name='bot-testing')
        await channel1.send('Task 1!')

    @task1.before_loop
    async def before_task1(self):
        await self.wait_until_ready()  # wait until the bot logs in

    @tasks.loop(seconds=3)
    async def task2(self):
        guild = discord.utils.get(self.guilds, name='Drury Lane')
        channel2 = discord.utils.get(guild.channels, name='bot-testing-2')
        await channel2.send('Task 2!')

    @task2.before_loop
    async def before_task2(self):
        await self.wait_until_ready()  # wait until the bot logs in


client = MyClient(intents=intents)

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

    if message.content.startswith('$refresh blargh'):
        output = run_script(SCRIPT_URLS['Tattoo Parlor'])
        
        print(output)

        channel = discord.utils.get(message.guild.channels, name='bot-testing-2')

        await channel.send(output)

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
