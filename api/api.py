# -*- coding:Utf-8 -*-
# !/usr/bin/env python3.5

"""

"""

############
#
#   GUILDS
#
############
from kyoukai import HTTPRequestContext

import api.API_commons as apcom
from cogs.utils import commons, prefs, scores

apcom.init()


@apcom.kyk.route("/guilds")
async def guilds(ctx: HTTPRequestContext):
    await commons.bot.wait_until_ready()
    resp = []
    for server in commons.bot.servers:
        # channels = {}
        # for channel in server.channels:
        #     channels[channel.id] = {
        #         "name"         : channel.name,
        #         "with_duckhunt": await is_channel_activated(channel)
        #     }
        # resp[server.id] = {
        #     "name"    : server.name,
        #     "channels": channels
        # }
        resp.append(server.id)

    return await apcom.prepare_resp(resp)


@apcom.kyk.route("/guilds/([^/]+)")  # /guild/server_id
async def guild_info(ctx: HTTPRequestContext, server_id: str):
    await commons.bot.wait_until_ready()
    server = commons.bot.get_server(server_id)
    servers = prefs.JSONloadFromDisk("channels.json")

    if server:
        channels = []
        for channel in server.channels:
            if apcom.is_channel_activated(channel):
                channels.append({
                                    "id": channel.id,
                                    "name": channel.name
                                    })
        settings = {}
        for setting in commons.defaultSettings.keys():
            settings[setting] = prefs.getPref(server, setting)

        resp = {
            "server_id": server_id,
            "name"     : server.name,
            "channels" : channels,
            "admins"   : servers[server_id]["admins"],
            "settings" : settings

        }

        return await apcom.prepare_resp(resp)

    else:
        resp = {}
        code = 404
        error_msg = "Guild not found on this bot"
        return await apcom.prepare_resp(resp, code=code, error_msg=error_msg)


@apcom.kyk.route("/guilds/([^/]+)/users")  # /guilds/server_id/users
async def guild_users(ctx: HTTPRequestContext, server_id: str):
    await commons.bot.wait_until_ready()
    server = commons.bot.get_server(server_id)

    if server:

        resp = {
            "server_id": server_id,
            "members"  : server.members
        }

        return await apcom.prepare_resp(resp)

    else:
        resp = {}
        code = 404
        error_msg = "Guild not found on this bot"
        return await apcom.prepare_resp(resp, code=code, error_msg=error_msg)


@apcom.kyk.route("/guilds/([^/]+)/channels")  # /guild/server_id/channels
async def guild_channels(ctx: HTTPRequestContext, server_id: str):
    await commons.bot.wait_until_ready()
    servers = prefs.JSONloadFromDisk("channels.json")
    server = commons.bot.get_server(server_id)
    channels = []
    if server:

        for channel in server.channels:
            activated = apcom.is_channel_activated(channel)
            channels.append({
                                "name"         : channel.name,
                                "id"           : channel.id,
                                "with_duckhunt": activated
                                })

        return await apcom.prepare_resp(channels)


    else:
        resp = {}
        code = 404
        error_msg = "Guild not found on this bot"
        return await apcom.prepare_resp(resp, code=code, error_msg=error_msg)


@apcom.kyk.route("/guilds/([^/]+)/channels/([^/]+)")  # /guilds/server_id/channel/channel_id
async def guild_channel(ctx: HTTPRequestContext, server_id: str, channel_id: str):
    await commons.bot.wait_until_ready()
    server = commons.bot.get_server(server_id)
    servers = prefs.JSONloadFromDisk("channels.json")

    if not server:
        resp = {}
        code = 404
        error_msg = "Guild not found on this bot"

        return await apcom.prepare_resp(resp, code=code, error_msg=error_msg)

    channel = server.get_channel(channel_id)
    if not channel:
        resp = {
            "server_id": server_id
        }
        code = 404
        error_msg = "Channel not found on this server"

        return await apcom.prepare_resp(resp, code=code, error_msg=error_msg)

    try:
        if channel_id in servers[server_id]["channels"]:
            activated = True
        else:
            activated = False
    except KeyError:
        activated = False

    if not activated:
        resp = {
            "server_id" : server_id,
            "channel_id": channel_id
        }
        code = 404
        error_msg = "DuckHunt is not enabled on this channel"

        return await apcom.prepare_resp(resp, code=code, error_msg=error_msg)
    i = 0
    resp = []
    for joueur in scores.topScores(ctx.message.channel):
        i += 1

        if (not "canardsTues" in joueur) or (joueur["canardsTues"] == 0) or ("canardTues" in joueur == False):
            joueur["canardsTues"] = 0
        if joueur["exp"] is None:
            joueur["exp"] = 0
        resp.append({
                        "position"    : i,
                        "user_id"     : joueur["id_"],
                        "exp"         : joueur["exp"],
                        "ducks_killed": joueur["canardsTues"],
                        "name"        : joueur["name"]
                        })

    return await apcom.prepare_resp(resp)


@apcom.kyk.route("/guilds/([^/]+)/channels/([^/]+)/users/([^/]+)")  # /guilds/server_id/channel/channel_id/users/user_id
async def guild_channel_users(ctx: HTTPRequestContext, server_id: str, channel_id: str, member_id: str):
    await commons.bot.wait_until_ready()
    server = commons.bot.get_server(server_id)

    if not server:
        resp = {}
        code = 404
        error_msg = "Guild not found on this bot"

        return await apcom.prepare_resp(resp, code=code, error_msg=error_msg)

    channel = server.get_channel(channel_id)
    if not channel:
        resp = {
            "server_id": server_id
        }
        code = 404
        error_msg = "Channel not found on this server"

        return await apcom.prepare_resp(resp, code=code, error_msg=error_msg)

    if not apcom.is_channel_activated(channel):
        resp = {
            "server_id" : server_id,
            "channel_id": channel_id
        }
        code = 404
        error_msg = "DuckHunt is not enabled on this channel"

        return await apcom.prepare_resp(resp, code=code, error_msg=error_msg)

    member = server.get_member(member_id)

    if not member:
        resp = {
            "server_id" : server_id,
            "channel_id": channel_id
        }
        code = 404
        error_msg = "User not found on this server"

        return await apcom.prepare_resp(resp, code=code, error_msg=error_msg)

    resp = apcom.get_user_scores(channel, member)
    return await apcom.prepare_resp(resp)


############
#
#   stats
#
############


@apcom.kyk.route("/stats/messages_recived")
async def messages_recived(ctx: HTTPRequestContext):
    resp = commons.number_messages
    return await apcom.prepare_resp(resp)


@apcom.kyk.root.errorhandler(500)
async def handle_500(ctx: HTTPRequestContext, exception_to_handle: Exception):
    return repr(exception_to_handle)
