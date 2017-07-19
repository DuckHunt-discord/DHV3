# -*- coding: utf-8 -*-
# !/usr/bin/env python3.6

"""
DuckHunt community bot
"""
import asyncio
import datetime
import json
import logging
import sys
import traceback
from collections import Counter

import os
from discord.ext import commands

try:
    import uvloop
except ImportError:
    pass
else:
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

initial_extensions = []
for extension in os.listdir("cogs"):
    if extension.endswith('.py'):
        try:
            initial_extensions.append("cogs." + extension.rstrip(".py"))
        except Exception as e:
            print('Failed to load extension {}\n{}: {}'.format(extension, type(e).__name__, e))

discord_logger = logging.getLogger('discord')
discord_logger.setLevel(logging.CRITICAL)
logger = logging.getLogger('selfbot')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
# file_handler = RotatingFileHandler('activity.log', 'a', 1000000, 1)
# file_handler.setLevel(logging.DEBUG)
# file_handler.setFormatter(formatter)
# logger.addHandler(file_handler)
steam_handler = logging.StreamHandler()
steam_handler.setLevel(logging.DEBUG)
steam_handler.setFormatter(formatter)
logger.addHandler(steam_handler)


help_attrs = dict(hidden=True, in_help=True, name="DONOTUSE")


def prefix(bot, message):
    return ["c!", "CDuckHunt", "cduckhunt", "cdh!", "cdh"]


bot = commands.Bot(command_prefix=prefix, description=__doc__, pm_help=None, help_attrs=help_attrs)


@bot.event
async def on_ready():
    logger.info('Logged in as:')
    logger.info('Username: ' + bot.user.name)
    logger.info('ID: ' + bot.user.id)
    if not hasattr(bot, 'uptime'):
        bot.uptime = datetime.datetime.utcnow()


@bot.event
async def on_resumed():
    pass


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    await bot.process_commands(message)


@bot.event
async def on_command(command, ctx):
    bot.commands_used[command.name] += 1
    logger.info(str(command) + " (" + ctx.message.clean_content + ") ")


@bot.event
async def on_command_error(error, ctx):
    if isinstance(error, commands.NoPrivateMessage):
        await bot.send_message(ctx.message.author, ':x: This command cannot be used in private messages.')
    elif isinstance(error, commands.DisabledCommand):
        await bot.send_message(ctx.message.author, ':x: Sorry. This command is disabled and cannot be used.')
    elif isinstance(error, commands.CommandInvokeError):
        sending = 'In {0.command.qualified_name}:\n'.format(ctx)
        sending += "\n".join(traceback.format_tb(error.original.__traceback__))
        sending += "\n"
        sending += "\n" + '{0.__class__.__name__}: {0}'.format(error.original)
        logger.error(sending)

        msg = await bot.send_message(ctx.message.channel, ":x: An error ({error}) happened in {command}, here is the traceback: ```\n{tb}\n```\n".format(**{
            "command": ctx.command.qualified_name,
            "error"  : error.original.__class__.__name__,
            "tb"     : "\n".join(traceback.format_tb(error.original.__traceback__, 4)),
        }))
    elif isinstance(error, commands.MissingRequiredArgument):
        await bot.send_message(ctx.message.channel, ":x: Missing a required argument. " + (("Help: \n```\n" + ctx.command.help + "\n```") if ctx.command.help else ""))
    elif isinstance(error, commands.BadArgument):
        await bot.send_message(ctx.message.channel, ":x: Bad argument provided. " + (("Help: \n```\n" + ctx.command.help + "\n```") if ctx.command.help else ""))


def load_credentials():
    with open('credentials.json') as f:
        return json.load(f)


if __name__ == '__main__':
    credentials = load_credentials()
    debug = any('debug' in arg.lower() for arg in sys.argv)
    if debug:
        bot.command_prefix = ['$']
        token = credentials.get('debug_token', credentials['token'])
    else:
        token = credentials['token']

    bot.client_id = credentials['client_id']
    bot.commands_used = Counter()
    bot.where = os.path.dirname(os.path.realpath(__file__)) + os.sep

    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
            logger.debug("Loaded: " + str(extension))
        except Exception as e:
            print('Failed to load extension {}\n{}: {}'.format(extension, type(e).__name__, e))

    bot.run(token)
    handlers = logger.handlers[:]
    for hdlr in handlers:
        hdlr.close()
        logger.removeHandler(hdlr)
