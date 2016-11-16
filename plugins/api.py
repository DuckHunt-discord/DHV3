# -*- coding:Utf-8 -*-
# !/usr/bin/env python3.5

"""

"""

import json

from kyoukai import HTTPRequestContext, Kyoukai

from cogs.utils import commons, prefs

kyk = Kyoukai("dh_api", debug=True)


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


@kyk.route("/servers/list")
async def index(ctx: HTTPRequestContext):
    servers = {}
    for server in commons.bot.servers:
        channels = {}
        for channel in server.channels:
            channels[channel.id] = {
                "name"         : channel.name,
                "with_duckhunt": await is_channel_activated(channel)
                }
        servers[server.id] = {
            "name"    : server.name,
            "channels": channels
            }

    return json.dumps(servers), 200, {
        "Content-Type": "application/json"
        }
