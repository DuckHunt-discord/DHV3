# -*- coding:Utf-8 -*-
# !/usr/bin/env python3.5

"""

"""
import json
import time

from kyoukai import HTTPRequestContext, Kyoukai

from cogs.utils import commons, prefs, scores

kyk = Kyoukai("dh_api", debug=False)
API_VERSION = "Duckhunt API, 0.0.1 ALPHA"

commons.api = kyk
commons.API_VERSION = API_VERSION


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


async def prepare_resp(resp_payload, code=200, error_msg="OK"):
    resp = {
        "generated_at": int(time.time()),
        "payload"     : resp_payload,
        "error"       : {
            "code"     : code,
            "error_msg": error_msg
        },
        "api_version" : API_VERSION
    }
    return json.dumps(resp), code, {
        "Content-Type": "application/json"
    }


############
#
#   GUILDS
#
############

@kyk.route("/guilds")
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

    return await prepare_resp(resp)


@kyk.route("/guilds/([^/]+)")  # /guild/server_id
async def guild_info(ctx: HTTPRequestContext, server_id: str):
    await commons.bot.wait_until_ready()
    server = commons.bot.get_server(server_id)
    servers = prefs.JSONloadFromDisk("channels.json")

    if server:
        channels = {}
        for channel in server.channels:
            channels[channel.id] = {
                "name"         : channel.name,
                "with_duckhunt": await is_channel_activated(channel)
            }
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

        return await prepare_resp(resp)

    else:
        resp = {}
        code = 404
        error_msg = "Guild not found on this bot"
        return await prepare_resp(resp, code=code, error_msg=error_msg)


@kyk.route("/guilds/([^/]+)/users")  # /guilds/server_id/users
async def guild_users(ctx: HTTPRequestContext, server_id: str):
    await commons.bot.wait_until_ready()
    server = commons.bot.get_server(server_id)

    if server:

        resp = {
            "server_id": server_id,
            "members"  : server.members
        }

        return await prepare_resp(resp)

    else:
        resp = {}
        code = 404
        error_msg = "Guild not found on this bot"
        return await prepare_resp(resp, code=code, error_msg=error_msg)


@kyk.route("/guilds/([^/]+)/channels")  # /guild/server_id/channels
async def guild_channels(ctx: HTTPRequestContext, server_id: str):
    await commons.bot.wait_until_ready()
    servers = prefs.JSONloadFromDisk("channels.json")
    server = commons.bot.get_server(server_id)
    channels = []
    if server:

        for channel in server.channels:
            try:
                if channel.id in servers[server_id]["channels"]:
                    activated = True
                else:
                    activated = False
            except KeyError:
                activated = False
            channels.append({
                                "name"         : channel.name,
                                "id"           : channel.id,
                                "with_duckhunt": activated
                                })

        return await prepare_resp(channels)


    else:
        resp = {}
        code = 404
        error_msg = "Guild not found on this bot"
        return await prepare_resp(resp, code=code, error_msg=error_msg)


@kyk.route("/guilds/([^/]+)/channels/([^/]+)")  # /guilds/server_id/channel/channel_id
async def guild_channel(ctx: HTTPRequestContext, server_id: str, channel_id: str):
    await commons.bot.wait_until_ready()
    server = commons.bot.get_server(server_id)
    servers = prefs.JSONloadFromDisk("channels.json")

    if not server:
        resp = {}
        code = 404
        error_msg = "Guild not found on this bot"

        return await prepare_resp(resp, code=code, error_msg=error_msg)

    channel = server.get_channel(channel_id)
    if not channel:
        resp = {
            "server_id": server_id
        }
        code = 404
        error_msg = "Channel not found on this server"

        return await prepare_resp(resp, code=code, error_msg=error_msg)

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

        return await prepare_resp(resp, code=code, error_msg=error_msg)
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

    return await prepare_resp(resp)


@kyk.route("/guilds/([^/]+)/channels/([^/]+)/users/([^/]+)")  # /guilds/server_id/channel/channel_id/users/user_id
async def guild_channel_users(ctx: HTTPRequestContext, server_id: str, channel_id: str, member_id: str):
    await commons.bot.wait_until_ready()
    server = commons.bot.get_server(server_id)
    servers = prefs.JSONloadFromDisk("channels.json")

    if not server:
        resp = {}
        code = 404
        error_msg = "Guild not found on this bot"

        return await prepare_resp(resp, code=code, error_msg=error_msg)

    channel = server.get_channel(channel_id)
    if not channel:
        resp = {
            "server_id": server_id
        }
        code = 404
        error_msg = "Channel not found on this server"

        return await prepare_resp(resp, code=code, error_msg=error_msg)

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

        return await prepare_resp(resp, code=code, error_msg=error_msg)

    member = server.get_member(member_id)

    if not member:
        resp = {
            "server_id" : server_id,
            "channel_id": channel_id
        }
        code = 404
        error_msg = "User not found on this server"

        return await prepare_resp(resp, code=code, error_msg=error_msg)

    resp = {
        "server_id"             : server_id,
        "channel_id"            : channel_id,
        "user_id"               : member.id,
        "name"                  : member.name,
        "nick"                  : member.nick,
        "discriminator"         : member.discriminator,
        "avatar_url"            : member.avatar_url,
        "weapon_confiscated"    : scores.getStat(channel, member, "confique"),
        "weapon_jammed"         : scores.getStat(channel, member, "enrayee"),
        "weapon_sabotaged"      : scores.getStat(channel, member, "sabotee"),
        "exp"                   : scores.getStat(channel, member, "exp"),
        "bullets"               : scores.getStat(channel, member, "balles"),
        "shots_without_ducks"   : scores.getStat(channel, member, "tirsSansCanards"),
        "ducks_killed"          : scores.getStat(channel, member, "canardsTues"),
        "best_time"             : scores.getStat(channel, member, "meilleurTemps", default=prefs.getPref(server, "time_before_ducks_leave")),
        "shoots_missed"         : scores.getStat(channel, member, "tirsManques"),
        "chargers"              : scores.getStat(channel, member, "chargeurs"),
        "banned"                : scores.getStat(channel, member, "banni"),
        "hunters_killed"        : scores.getStat(channel, member, "chasseursTues"),
        "super_ducks_killed"    : scores.getStat(channel, member, "superCanardsTues"),
        "last_giveback"         : scores.getStat(channel, member, "lastGiveback"),
        "wet"                   : scores.getStat(channel, member, "mouille"),
        "time_explosive_ammo"   : scores.getStat(channel, member, "munExplo"),
        "time_AP_ammo"          : scores.getStat(channel, member, "munAP_"),
        "time_grease"           : scores.getStat(channel, member, "graisse"),
        "time_life_insurence"   : scores.getStat(channel, member, "AssuranceVie"),
        "time_clover"           : scores.getStat(channel, member, "trefle"),
        "clover_exp"            : scores.getStat(channel, member, "trefle_exp"),
        "time_infrared_detector": scores.getStat(channel, member, "detecteurInfra"),
        "time_silencer"         : scores.getStat(channel, member, "silencieux")
    }
    return await prepare_resp(resp)


############
#
#   stats
#
############


@kyk.route("/stats/messages_recived")
async def messages_recived(ctx: HTTPRequestContext):
    resp = commons.number_messages
    return await prepare_resp(resp)


@kyk.root.errorhandler(500)
async def handle_500(ctx: HTTPRequestContext, exception_to_handle: Exception):
    return repr(exception_to_handle)
