# -*- coding:Utf-8 -*-
# !/usr/bin/env python3.5

"""

"""

import json

from kyoukai import HTTPRequestContext, Kyoukai

from cogs.utils import commons, prefs

kyk = Kyoukai("dh_api", debug=False)


async def is_channel_activated(channel):
    servers = prefs.JSONloadFromDisk("channels.json")

    try:
        if channel.id in servers[channel.server.id]["channels"]:
            activated = True
        else:
            activated = False
    except KeyError:
        activated = False

    return activated


@kyk.route("/guilds")
async def guilds(ctx: HTTPRequestContext):
    resp = {}
    for server in commons.bot.servers:
        channels = {}
        for channel in server.channels:
            channels[channel.id] = {
                "name"         : channel.name,
                "with_duckhunt": await is_channel_activated(channel)
            }
        resp[server.id] = {
            "name"    : server.name,
            "channels": channels
        }

    return json.dumps(resp), 200, {
        "Content-Type": "application/json"
    }


@kyk.route("/guilds/\d+")
async def guild_info(ctx: HTTPRequestContext, id: int):
    server = commons.bot.get_server(id)
    servers = prefs.JSONloadFromDisk("channels.json")

    if server:

        channels = {}
        for channel in server.channels:
            channels[channel.id] = {
                "name"         : channel.name,
                "with_duckhunt": await is_channel_activated(channel)
            }
        resp = {
            "id"      : id,
            "name"    : server.name,
            "channels": channels,
            "admins"  : servers[id]["admins"]
        }

    else:
        resp = {
            "message": "Error, guild not found"
            }

    return json.dumps(resp), 404, {
        "Content-Type": "application/json"
    }
