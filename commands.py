# commands.py
#
# Top-level handler for all bot commands.

import logging

import vistani_market
import tattoo_parlor

PREFIX = '$pw '

log = logging.getLogger('app.commands')

async def handle(message):
    """
    Parse a bot command and route it to the correct handler along with any arguments. 
    """
    log.debug(f'Handling: "{message.content}"')

    # Obviously a simple switch statement won't be enough for long 
    # if we add more commands and real arguments.
    match message.content.removeprefix(PREFIX):
        case 'hello':
            await _handle_hello(message)
        case 'help' | '-help' | '--help':
            await _handle_help(message)
        case 'refresh vistani':
            await _handle_refresh_vistani(message)
        case 'refresh tattoo':
            await _handle_refresh_tattoo(message)
        case _:
            await _handle_unknown_command(message)

async def _handle_hello(message):
    await message.channel.send('*The creepy doll slowly gives you a thumbs up.*')

async def _handle_help(message):
    # TODO
    await message.channel.send('Sorry, "help" not implemented yet!')

async def _handle_refresh_vistani(message):
    """
    Regenerate the Vistani Market inventory in the same channel as the command.
    It's for testing, so let's not spam people with '@Players' pings.
    """
    output = vistani_market.generate_inventory()
    await vistani_market.post_inventory(output, message.channel, mute_announcement=True)

async def _handle_refresh_tattoo(message):
    """
    Regenerate the Tattoo Parlor inventory in the same channel as the command.
    It's for testing, so let's not spam people with '@Players' pings.
    """
    output = tattoo_parlor.generate_inventory()
    await tattoo_parlor.post_inventory(output, message.channel, mute_announcement=True)

async def _handle_unknown_command(message):
    command = message.content.removeprefix(PREFIX)
    await message.channel.send(f'Unrecognized command: "{command}"')
