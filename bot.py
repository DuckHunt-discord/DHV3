import asyncio
import datetime
import json
import locale
import logging
import random
import sys
import time
import traceback
from collections import Counter

import discord
from discord.ext import commands

from cogs.utils import commons

try:
    locale.setlocale(locale.LC_ALL, 'fr_FR')
except locale.Error:
    pass

commons.init()

from cogs.utils.commons import _

description = """DuckHunt, a game about killing ducks"""

initial_extensions = ['cogs.admin', 'cogs.carbonitex', 'cogs.exp', 'cogs.meta', 'cogs.serveradmin', 'cogs.shoot']

discord_logger = logging.getLogger('discord')
discord_logger.setLevel(logging.CRITICAL)

log = logging.getLogger()
log.setLevel(logging.INFO)
handler = logging.FileHandler(filename='dh.log', encoding='utf-8', mode='w')
log.addHandler(handler)

help_attrs = dict(hidden=True, in_help=True, name="DONOTUSE")


def prefix(bot, message):
    return [':duck:', "🦆" "DuckHunt", "duckhunt"] + list(prefs.getPref(message.server, "prefix"))


bot = commands.Bot(command_prefix=prefix, description=description, pm_help=None, help_attrs=help_attrs)
commons.bot = bot

logger = commons.logger


@bot.event
async def on_command_error(error, ctx):
    language = prefs.getPref(ctx.message.server, "language")
    if isinstance(error, commands.NoPrivateMessage):
        await bot.send_message(ctx.message.author, _(':x: This command cannot be used in private messages.', language))
    elif isinstance(error, commands.DisabledCommand):
        await bot.send_message(ctx.message.author, _(':x: Sorry. This command is disabled and cannot be used.', language))
    elif isinstance(error, commands.CommandInvokeError):
        print('In {0.command.qualified_name}:'.format(ctx), file=sys.stderr)
        traceback.print_tb(error.original.__traceback__)
        print('{0.__class__.__name__}: {0}'.format(error.original), file=sys.stderr)
        await comm.message_user(ctx.message, _(":x: An error ({error}) happened in {command}, here is the traceback : ```\n{tb}\n```", language).format(**{
            "command": ctx.command.qualified_name,
            "error"  : error.original.__class__.__name__,
            "tb"     : "\n".join(traceback.format_tb(error.original.__traceback__))
        }))
    elif isinstance(error, commands.MissingRequiredArgument):
        await comm.message_user(ctx.message, _(":x: Missing a required argument. ", language) + (("Help : \n```\n" + ctx.command.help + "\n```") if ctx.command.help else ""))
    elif isinstance(error, commands.BadArgument):
        await comm.message_user(ctx.message, _(":x: Bad argument provided. ", language) + (("Help : \n```\n" + ctx.command.help + "\n```") if ctx.command.help else ""))
        # elif isinstance(error, commands.CheckFailure):
        # await comm.message_user(ctx.message, _(":x: You are not an admin/owner, you don't have enough exp to use this command, or you are banned from the channel, so you can't use this command. ", language) + (("Help : \n```\n" + ctx.command.help + "\n```") if ctx.command.help else ""))


@bot.event
async def on_ready():
    logger.info('Logged in as:')
    logger.info('Username: ' + bot.user.name)
    logger.info('ID: ' + bot.user.id)
    await bot.change_presence(game=discord.Game(name="Killing ducks | !help"))
    if not hasattr(bot, 'uptime'):
        bot.uptime = datetime.datetime.utcnow()


@bot.event
async def on_resumed():
    logger.info('resumed...')


@bot.event
async def on_command(command, ctx):
    bot.commands_used[command.name] += 1
    await comm.logwithinfos_message(ctx.message, str(command))
    # message = ctx.message
    # destination = None
    # if message.channel.is_private:
    #    destination = 'Private Message'
    # else:
    #    destination = '#{0.channel.name} ({0.server.name})'.format(message)
    #
    # log.info('{0.timestamp}: {0.author.name} in {1}: {0.content}'.format(message, destination))


@bot.event
async def on_message(message):
    commons.number_messages += 1
    if message.author.bot:
        return

    # await comm.logwithinfos_message(message, message.content)
    await bot.process_commands(message)


@bot.event
async def on_channel_delete(channel):
    await ducks.del_channel(channel)



@bot.event
async def on_server_remove(server):
    for channel in server.channels:
        await ducks.del_channel(channel)


def load_credentials():
    with open('credentials.json') as f:
        return json.load(f)


async def mainloop():
    try:
        await bot.wait_until_ready()
        planday = 0
        next_duck = await get_next_duck()
        while not bot.is_closed:
            now = time.time()
            if int((int(now)) / 86400) != planday:
                # database.giveBack(logger)
                planday = int(int(now) / 86400)
                await planifie()
                next_duck = await get_next_duck()

            if int(now) % 60 == 0 and next_duck["time"] != 0:
                timetonext = next_duck["time"] - now
                await comm.logwithinfos(next_duck["channel"], None, "Next duck : {time} (in {timetonext} sec) ".format(**{
                    "timetonext": timetonext,
                    "time"      : next_duck["time"]
                }))
                logger.debug("Current ducks : {canards}".format(**{
                    "canards": len(commons.ducks_spawned)
                }))

            if next_duck["time"] < now and next_duck["time"] != 0:  # CANARD !
                await spawn_duck(next_duck)
                next_duck = await get_next_duck()

            if next_duck["time"] == 0:  # No more ducks
                next_duck = await get_next_duck()

            for canard in commons.ducks_spawned:
                if int(canard["time"]) + int(prefs.getPref(canard["channel"].server, "time_before_ducks_leave")) < int(now):  # Canard qui se barre
                    await comm.logwithinfos(canard["channel"], None, "Duck of {time} stayed for too long. (it's {now}, and it should have stayed until {shouldwaitto}).".format(**{
                        "time"        : canard["time"],
                        "now"         : now,
                        "shouldwaitto": str(int(canard["time"] + prefs.getPref(canard["channel"].server, "time_before_ducks_leave")))
                    }))
                    try:
                        await bot.send_message(canard["channel"], _(random.choice(commons.canards_bye), language=prefs.getPref(canard["channel"].server, "language")))
                    except:
                        pass
                    try:
                        commons.ducks_spawned.remove(canard)
                    except:
                        logger.warning("Oops, error when removing duck : " + str(canard))

            await asyncio.sleep(1)
    except:
        logger.exception("")
        raise


if __name__ == '__main__':
    credentials = load_credentials()
    debug = any('debug' in arg.lower() for arg in sys.argv)
    if debug:
        bot.command_prefix = '$'
        token = credentials.get('debug_token', credentials['token'])
    else:
        token = credentials['token']

    bot.client_id = credentials['client_id']
    bot.commands_used = Counter()
    bot.bots_key = credentials['bots_key']
    ## POST INIT IMPORTS ##
    from cogs.utils.ducks import get_next_duck, planifie, spawn_duck, allCanardsGo
    from cogs.utils import prefs, comm
    from cogs.utils import ducks
    import api.api as api




    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            logger.exception('Failed to load extension {}\n{}: {}'.format(extension, type(e).__name__, e))
    bot.loop.create_task(mainloop())
    # noinspection PyBroadException
    try:

        bot.loop.create_task(api.apcom.kyk.start(port=5566))
        bot.loop.run_until_complete(bot.start(token))
    except KeyboardInterrupt:
        logger.warning("Shutdown in progress")
    except:
        logger.exception("Unknown error, restarting")

    finally:
        # noinspection PyBroadException
        try:
            bot.loop.run_until_complete(allCanardsGo())
        except:
            pass
        handlers = log.handlers[:]
        for hdlr in handlers:
            hdlr.close()
            log.removeHandler(hdlr)
        bot.loop.run_until_complete(bot.logout())

    asyncio.sleep(3)
    bot.loop.close()
