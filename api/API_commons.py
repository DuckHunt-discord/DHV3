# -*- coding:Utf-8 -*-
# !/usr/bin/env python3.5

"""

"""
import json

import discord
from kyoukai import Kyoukai

from cogs.utils import prefs, scores

global kyk, API_VERSION
kyk = Kyoukai("dh_api", debug=False)
API_VERSION = "Duckhunt API, 0.0.1 ALPHA"

async def is_player_check(member, channel=None):
    if isinstance(member, discord.Member):
        member = scores.getChannelTable(channel).find_one(id_=member.id)

    if (member.get('shoots_fired', 0) or 0) > 0:
        return True
    else:
        return False

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


async def prepare_resp(resp_payload, code=200):
    return json.dumps(resp_payload), code, {
        "Content-Type": "application/json"
    }
