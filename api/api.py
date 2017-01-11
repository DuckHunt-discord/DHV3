# -*- coding:Utf-8 -*-
# !/usr/bin/env python3.5

"""

"""

############
#
#   GUILDS
#
#   Le premier qui me dit que mon code est laid, il se prend une paire de claques :D
############
from kyoukai import HTTPRequestContext
from discord.enums import ChannelType
from collections import defaultdict
from operator import attrgetter, itemgetter

import api.API_commons as apcom
from cogs.utils import commons, prefs, scores

@apcom.kyk.route("/guilds/?")
async def guilds(ctx: HTTPRequestContext):
    await commons.bot.wait_until_ready()

    servers = []
    stats = defaultdict(int)

    for server in commons.bot.servers:
        channel_count = 0
        player_count = 0
        players = []

        global_scores = prefs.getPref(server, "global_scores")

        for channel in server.channels:
            activated = await apcom.is_channel_activated(channel)

            if activated and channel.type == ChannelType.text:
                channel_count += 1
                stats['channel_count'] += 1

        if global_scores:
            first_chan = next(iter(server.channels))

            for member in server.members:
                if await apcom.is_player_check(first_chan, member):
                    player_count += 1
                    stats['player_count'] += 1

                    players.append({
                        "id": member.id,
                        "name": member.name,
                        "kills": scores.getStat(first_chan, member, "canardsTues"),
                        "exp": scores.getStat(first_chan, member, "exp"),
                        "best_time": scores.getStat(first_chan, member, "meilleurTemps", default=prefs.getPref(first_chan.server, "time_before_ducks_leave"))
                    })

                    stats['all_killed_ducks'] += scores.getStat(first_chan, member, "canardsTues") + scores.getStat(first_chan, member, "superCanardsTues")
                    stats['killed_ducks'] += scores.getStat(first_chan, member, "canardsTues")
                    stats['killed_super_ducks'] += scores.getStat(first_chan, member, "superCanardsTues")
                    stats['killed_players'] += scores.getStat(first_chan, member, "chasseursTues")
                    stats['missed_shots'] += scores.getStat(first_chan, member, "tirsManques")
        else:
            for member in server.members:
                counted = False

                for channel in server.channels:
                    activated = await apcom.is_channel_activated(channel)

                    if activated and channel.type == ChannelType.text:
                        if await apcom.is_player_check(channel, member):
                            if not counted:
                                player_count += 1
                                stats['player_count'] += 1

                            players.append({
                                "id": member.id,
                                "name": member.name,
                                "kills": scores.getStat(channel, member, "canardsTues") + scores.getStat(channel, member, "superCanardsTues"),
                                "exp": scores.getStat(channel, member, "exp"),
                                "best_time": scores.getStat(channel, member, "meilleurTemps", default=prefs.getPref(channel.server, "time_before_ducks_leave"))
                            })

                            stats['all_killed_ducks'] += scores.getStat(channel, member, "canardsTues") + scores.getStat(channel, member, "superCanardsTues")
                            stats['killed_ducks'] += scores.getStat(channel, member, "canardsTues")
                            stats['killed_super_ducks'] += scores.getStat(channel, member, "superCanardsTues")
                            stats['killed_players'] += scores.getStat(channel, member, "chasseursTues")
                            stats['missed_shots'] += scores.getStat(channel, member, "tirsManques")
                            counted = True

        if channel_count > 0 and player_count > 0:
            players.sort(key=lambda x: x['name'])
            players.sort(key=lambda x: x['best_time'])
            players.sort(key=lambda x: x['exp'], reverse=True)
            players.sort(key=lambda x: x['kills'], reverse=True)

            servers.append({
                                "id": server.id,
                                "name": server.name,
                                "icon": server.icon_url or None,
                                "channel_count": channel_count,
                                "player_count": player_count,
                                "best_player": players[0]
                            })

    servers.sort(key=lambda x: x['name'])
    servers.sort(key=lambda x: x['player_count'], reverse=True)

    stats['server_count'] = len(servers)

    resp = {
        "servers": servers,
        "stats": stats
    }

    return await apcom.prepare_resp(resp)

@apcom.kyk.route("/guilds/([^/]+)/?")  # /guild/server_id
async def guild_info(ctx: HTTPRequestContext, server_id: str):
    await commons.bot.wait_until_ready()

    server = commons.bot.get_server(server_id)

    if server:
        player_count = 0
        channels = []
        players = []

        global_scores = prefs.getPref(server, "global_scores")

        stats = defaultdict(int)

        #settings = []

        #for setting in commons.defaultSettings.keys():
            #settings[setting] = prefs.getPref(server, setting)

        for channel in server.channels:
            activated = await apcom.is_channel_activated(channel)

            if activated and channel.type == ChannelType.text:
                channels.append({
                                    "id": channel.id,
                                    "name": channel.name
                                })

        if global_scores:
            first_chan = next(iter(server.channels))

            for member in server.members:
                if await apcom.is_player_check(first_chan, member):
                    player_count += 1
                    stats['player_count'] += 1

                    players.append({
                        "id": member.id,
                        "name": member.name,
                        "kills": scores.getStat(first_chan, member, "canardsTues"),
                        "exp": scores.getStat(first_chan, member, "exp"),
                        "best_time": scores.getStat(first_chan, member, "meilleurTemps", default=prefs.getPref(server, "time_before_ducks_leave"))
                    })

                    stats['all_killed_ducks'] += scores.getStat(first_chan, member, "canardsTues") + scores.getStat(first_chan, member, "superCanardsTues")
                    stats['killed_ducks'] += scores.getStat(first_chan, member, "canardsTues")
                    stats['killed_super_ducks'] += scores.getStat(first_chan, member, "superCanardsTues")
                    stats['killed_players'] += scores.getStat(first_chan, member, "chasseursTues")
                    stats['missed_shots'] += scores.getStat(first_chan, member, "tirsManques")
        else:
            for member in server.members:
                counted = False

                for channel in server.channels:
                    activated = await apcom.is_channel_activated(channel)

                    if activated and channel.type == ChannelType.text:
                        if await apcom.is_player_check(channel, member):
                            if not counted:
                                player_count += 1
                                stats['player_count'] += 1

                            players.append({
                                "id": member.id,
                                "name": member.name,
                                "kills": scores.getStat(channel, member, "canardsTues") + scores.getStat(channel, member, "superCanardsTues"),
                                "exp": scores.getStat(channel, member, "exp"),
                                "best_time": scores.getStat(channel, member, "meilleurTemps", default=prefs.getPref(server, "time_before_ducks_leave"))
                            })

                            stats['all_killed_ducks'] += scores.getStat(channel, member, "canardsTues") + scores.getStat(channel, member, "superCanardsTues")
                            stats['killed_ducks'] += scores.getStat(channel, member, "canardsTues")
                            stats['killed_super_ducks'] += scores.getStat(channel, member, "superCanardsTues")
                            stats['killed_players'] += scores.getStat(channel, member, "chasseursTues")
                            stats['missed_shots'] += scores.getStat(channel, member, "tirsManques")

                            counted = True

        players.sort(key=lambda x: x['name'])
        players.sort(key=lambda x: x['best_time'])
        players.sort(key=lambda x: x['exp'], reverse=True)
        players.sort(key=lambda x: x['kills'], reverse=True)

        info = {
            "id": server.id,
            "name": server.name,
            "channels": channels,
            "best_player": players[0]
        }

        resp = {
            "server": info,
            "stats": stats
        }

        return await apcom.prepare_resp(resp)
    else:
        return await apcom.prepare_resp(None, 404, "Guild not found.")


@apcom.kyk.route("/guilds/([^/]+)/users/?")  # /guilds/server_id/users
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
        return await apcom.prepare_resp(None, 404, "Guild not found.")


"""@apcom.kyk.route("/guilds/([^/]+)/channels/?")  # /guild/server_id/channels
async def guild_channels(ctx: HTTPRequestContext, server_id: str):
    await commons.bot.wait_until_ready()
    servers = prefs.JSONloadFromDisk("channels.json")
    server = commons.bot.get_server(server_id)
    channels = []

    if server:
        for channel in server.channels:
            activated = await apcom.is_channel_activated(channel)

            if activated and channel.type == ChannelType.text:
                channels.append({
                                    "id"   : channel.id,
                                    "name" : channel.name
                                })

        return await apcom.prepare_resp(channels)
    else:
        return await apcom.prepare_resp({}, 404, "Guild not found.")"""

@apcom.kyk.route("/guilds/([^/]+)/channels/([^/]+)/?")  # /guilds/server_id/channel/channel_id
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


@apcom.kyk.route("/guilds/([^/]+)/channels/([^/]+)/users/([^/]+)/?")  # /guilds/server_id/channel/channel_id/users/user_id
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

    if not await apcom.is_channel_activated(channel):
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

    resp = await apcom.get_user_scores(channel, member)
    return await apcom.prepare_resp(resp)


############
#
#   stats
#
############


@apcom.kyk.route("/stats/messages_recived/?")
async def messages_recived(ctx: HTTPRequestContext):
    resp = commons.number_messages
    return await apcom.prepare_resp(resp)


@apcom.kyk.root.errorhandler(500)
async def handle_500(ctx: HTTPRequestContext, exception_to_handle: Exception):
    return repr(exception_to_handle)
