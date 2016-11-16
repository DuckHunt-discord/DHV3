# -*- coding:Utf-8 -*-
# !/usr/bin/env python3.5
"""
DHV2 -- comm
"""

import discord
import requests

from . import commons, prefs


async def paste(data, ext):  # TODO: Async problems ?
    HASTEBIN_SERVER = 'http://api-d.com:7777'
    r = requests.post(HASTEBIN_SERVER + '/documents', data=data.encode("UTF-8"))
    j = r.json()
    if r.status_code is requests.codes.ok:
        return '{}/{}.{}'.format(HASTEBIN_SERVER, j['key'], ext)
    else:
        raise ResourceWarning(j['message'], r)


async def logwithinfos_ctx(ctx_obj, log_str):
    await logwithinfos_message(ctx_obj.message, log_str)


async def logwithinfos_message(message_obj: discord.Message, log_str: str):
    await logwithinfos(message_obj.channel, author=message_obj.author, log_str=log_str)


async def logwithinfos(channel: discord.Channel, author=None, log_str=""):
    commons.logger.debug(((channel.server.name.center(16, " ") if len(channel.server.name) < 16 else channel.server.name[:16]) if channel else "XX") + " :: " + ((("#" + channel.name).center(16, " ") if len(channel.name) < 16 else channel.name[:16]) if channel else "XX") + " :: " + ("<" + author.name + "> " if author else "") + log_str)


async def message_user(message, toSend, forcePv=False):
    if len(toSend) > 1950:
        await logwithinfos_message(message, "Creating a paste...")
        toSend = await paste(toSend.replace("```", ""), "py")
        # logger.info(_("Message trop long, envoi sur hastebin avec le lien : ") + toSend)
        await logwithinfos_message(message, "Paste envoyé, lien : " + str(toSend))
    if prefs.getPref(message.server, "pm_most_messages") or forcePv == True:
        try:
            await commons.bot.send_message(message.author, toSend)
        except discord.errors.Forbidden:
            try:
                await commons.bot.send_message(message.channel, str(message.author.mention) + "403 Permission denied (can't send private messages to this user)")
                await logwithinfos_message(message, "Impossible to send private messages to this user")
            except:
                await logwithinfos_message(message, "Impossible to send messages in the channel")
    else:
        try:
            await commons.bot.send_message(message.channel, str(message.author.mention) + " > " + toSend)
        except:
            await logwithinfos_message(message, "Impossible to send messages in the channel")
