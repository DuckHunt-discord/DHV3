# -*- coding:Utf-8 -*-
# !/usr/bin/env python3.5

"""

"""
import random
import time

import discord

from cogs.utils import comm, commons, prefs
from cogs.utils.comm import logwithinfos
from cogs.utils.prefs import getPref
from .commons import _

logger = commons.logger
bot = commons.bot


async def allCanardsGo():
    for canard in commons.ducks_spawned:
        try:
            await bot.send_message(canard["channel"], _(random.choice(commons.canards_bye), language=getPref(canard["channel"].server, "language")))
            await logwithinfos(canard["channel"], None, "Force-leaving of duck " + str(canard))
        except:
            await logwithinfos(canard["channel"], None, "Force-leaving of duck FAILED " + str(canard))
            logger.exception("Here is why : ")

async def planifie(channel_obj: discord.Channel = None):
    if not channel_obj:
        logger.debug("Replanning")
        planification_ = {}
        now = time.time()
        thisDay = now - (now % 86400)
        servers = prefs.JSONloadFromDisk("channels.json", default="{}")
        for server_ in servers.keys():
            server = bot.get_server(str(server_))
            if not server:
                logger.debug("Non-existant server : " + str(server_))

            elif not "channels" in servers[server.id]:
                await comm.logwithinfos(server.default_channel, log_str="Server not configured : " + server.id)
                try:
                    await bot.send_message(server, "The bot is not configured properly, please check the config or contact Eyesofcreeper#4758 | https://discord.gg/2BksEkV")
                    await comm.logwithinfos(server.default_channel, log_str="Unconfigured message sent...")
                except:
                    await comm.logwithinfos(server.default_channel, log_str="Error sending the unconfigured message to the default channel on the server.")

                pass
            else:
                for channel_ in servers[server.id]["channels"]:
                    channel = server.get_channel(str(channel_))
                    if channel:
                        permissions = channel.permissions_for(server.me)
                        if permissions.read_messages and permissions.send_messages:
                            # logger.debug("Adding channel : {id} ({ducks_per_day} c/j)".format(**{
                            #    "id"           : channel.id,
                            #    "ducks_per_day": prefs.getPref(server, "ducks_per_day")
                            # }))
                            templist = []
                            for id_ in range(1, prefs.getPref(server, "ducks_per_day") + 1):
                                templist.append(int(thisDay + random.randint(0, 86400)))
                            planification_[channel] = sorted(templist)
                        else:
                            await comm.logwithinfos(channel, log_str="Error adding channel to planification : no read/write permissions!")
                    else:
                        pass
        commons.ducks_planned = planification_  # {"channel":[time objects]}

    else:
        templist = []
        now = time.time()
        thisDay = now - (now % 86400)
        permissions = channel_obj.permissions_for(channel_obj.server.me)
        if permissions.read_messages and permissions.send_messages:
            for id_ in range(1, prefs.getPref(channel_obj.server, "ducks_per_day") + 1):
                templist.append(int(thisDay + random.randint(0, 86400)))
        else:
            await comm.logwithinfos(channel_obj, log_str="Error adding channel to planification : no read/write permissions!")
        commons.ducks_planned[channel_obj] = sorted(templist)




async def get_next_duck():
    now = time.time()
    prochaincanard = {
        "time"   : 0,
        "channel": None
    }
    # logger.debug(commons.ducks_planned)
    for channel in commons.ducks_planned.keys():  # Determination du prochain canard
        for canard in commons.ducks_planned[channel]:
            if canard > now:
                if canard < prochaincanard["time"] or prochaincanard["time"] == 0:
                    prochaincanard = {
                        "time"   : canard,
                        "channel": channel
                    }
    timetonext = prochaincanard["time"] - time.time()

    if not prochaincanard["channel"]:
        thisDay = now - (now % 86400)
        logger.debug("No more ducks for today, wait for {demain} sec".format(**{
            "demain": thisDay + 86400 - time.time()
        }))

    else:
        await comm.logwithinfos(prochaincanard["channel"], log_str="Next duck at {time} (in {timetonext} sec)".format(**{
            "timetonext": timetonext,
            "time"      : prochaincanard["time"]
        }))

    return prochaincanard


async def spawn_duck(duck):
    servers = prefs.JSONloadFromDisk("channels.json", default="{}")
    try:
        if servers[duck["channel"].server.id]["detecteur"].get(duck["channel"].id, False):
            for playerid in servers[duck["channel"].server.id]["detecteur"][duck["channel"].id]:
                player = discord.utils.get(duck["channel"].server.members, id=playerid)
                try:
                    await bot.send_message(player, _("There is a duck on #{channel}", prefs.getPref(duck["channel"].server, "lang")).format(**{
                        "channel": duck["channel"].name
                    }))
                    await comm.logwithinfos(duck["channel"], player, "Sending a duck notification")
                except:
                    await comm.logwithinfos(duck["channel"], player, "Error sending the duck notification")
                    pass

            servers[duck["channel"].server.id]["detecteur"].pop(duck["channel"].id)
            prefs.JSONsaveToDisk(servers, "channels.json")
    except KeyError:
        pass

    chance = random.randint(0, 100)
    if chance <= prefs.getPref(duck["channel"].server, "super_ducks_chance"):
        life = random.randint(prefs.getPref(duck["channel"].server, "super_ducks_minlife"), prefs.getPref(duck["channel"].server, "super_ducks_maxlife"))
        duck["isSC"] = True
        duck["SCvie"] = life
        duck["level"] = life
    else:
        duck["isSC"] = False
        duck["level"] = 1
        duck["SCvie"] = 1

    await comm.logwithinfos(duck["channel"], None, "New duck : " + str(duck))
    duck["time"] = time.time()
    if prefs.getPref(duck["channel"].server, "randomize_ducks"):
        canard_str = random.choice(commons.canards_trace) + "  " + random.choice(commons.canards_portrait) + "  " + _(random.choice(commons.canards_cri), language=prefs.getPref(duck["channel"].server, "language"))
    else:
        canard_str = "-,,.-'\`'°-,,.-'\`'° /_^<   QUAACK"
    try:
        await bot.send_message(duck["channel"], canard_str)
    except:
        pass
    commons.ducks_spawned.append(duck)
    logger.debug(duck)


async def del_channel(channel):
    servers = prefs.JSONloadFromDisk("channels.json")
    try:
        if str(channel.id) in servers[channel.server.id]["channels"]:
            await comm.logwithinfos(channel, author=None, log_str="Deleting channel {name} | {id} from the json file...".format(**{
                "id"  : channel.id,
                "name": channel.name
            }))
            servers[channel.server.id]["channels"].remove(channel.id)
            prefs.JSONsaveToDisk(servers, "channels.json")
            try:
                commons.ducks_planned.pop(channel.id)
                pass
            except:
                pass
            for duck in commons.ducks_spawned[:]:
                if duck["channel"] == channel:
                    commons.ducks_spawned.remove(duck)
    except KeyError:
        pass
