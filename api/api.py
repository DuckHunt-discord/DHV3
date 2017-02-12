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

# TODO: vérifier la validité des serv/chan ids à chaque fois

from kyoukai import HTTPRequestContext
from discord.enums import ChannelType
from collections import defaultdict

import api.API_commons as apcom
from cogs.utils import commons, prefs, scores

@apcom.kyk.route("/guilds/?")
async def guilds(ctx: HTTPRequestContext):
    await commons.bot.wait_until_ready()

    servers = []
    server_count = 0

    for server in commons.bot.servers:
        global_scores = prefs.getPref(server, "global_scores")
        channel_count = 0
        hasPlayers = False

        for channel in server.channels:
            activated = await apcom.is_channel_activated(channel)
            if activated and channel.type == ChannelType.text:
                channel_count += 1
                if not hasPlayers:
                    table = scores.getChannelTable(channel)
                    for member in table:
                        if await apcom.is_player_check(member=member, isRow=True):
                            hasPlayers = True
                            break

        if channel_count > 0 and hasPlayers:
            server_count += 1
            servers.append({
                                "id": server.id,
                                "name": server.name,
                                "icon": server.icon_url or None
                            })

    servers.sort(key=lambda x: x['name'])

    resp = {
        "servers": servers,
        "server_count": server_count
    }

    return await apcom.prepare_resp(resp)

@apcom.kyk.route("/guilds/([^/]+)/?")  # /guilds/server_id
async def guild_info(ctx: HTTPRequestContext, server_id: str):
    await commons.bot.wait_until_ready()

    server = commons.bot.get_server(server_id)

    if server:
        player_count = 0
        channels = []
        players = []

        global_scores = prefs.getPref(server, "global_scores")

        stats = defaultdict(int)

        if not global_scores:
            for channel in server.channels:
                activated = await apcom.is_channel_activated(channel)
                if activated and channel.type == ChannelType.text:
                    table = scores.getChannelTable(channel)
                    for member in table:
                        if await apcom.is_player_check(member=member, isRow=True):
                            channels.append({
                                                "id": channel.id,
                                                "name": channel.name
                                            })
                            break

            channels.sort(key=lambda x: x['name'])

            resp = {
                "server": {"name": server.name, "channels": channels},
                "global_scores": global_scores
            }
        else:
            players = []

            table = scores.getChannelTable(next(iter(server.channels)))
            for member in table:
                if await apcom.is_player_check(member=member, isRow=True):
                    player = server.get_member(member['id_'])

                    players.append({
                        "id": player.id,
                        "name": player.display_name,
                        "avatar": player.avatar_url or player.default_avatar_url
                    })

            resp = {
                "server": {"id": server.id, "name": server.name},
                "players": players,
                "global_scores": global_scores
            }

        return await apcom.prepare_resp(resp)
    else:
        return await apcom.prepare_resp(None, 404, "Guild not found.")


@apcom.kyk.route("/guilds/([^/]+)/channels/([^/]+)/?")  # /guilds/server_id/channels/channel_id
async def guild_channel(ctx: HTTPRequestContext, server_id: str, channel_id: str):
    await commons.bot.wait_until_ready()

    server = commons.bot.get_server(server_id)

    if server:
        channel = server.get_channel(channel_id)
        if channel:
            activated = await apcom.is_channel_activated(channel)
            if activated:
                players = []

                table = scores.getChannelTable(channel)
                for member in table:
                    if await apcom.is_player_check(member=member, isRow=True):
                        player = server.get_member(member['id_'])

                        players.append({
                            "id": player.id,
                            "name": player.display_name,
                            "avatar": player.avatar_url or player.default_avatar_url
                        })
            else:
                return await apcom.prepare_resp(None, 404, "Channel not activated.")
        else:
            return await apcom.prepare_resp(None, 404, "Channel not found.")
    else:
        return await apcom.prepare_resp(None, 404, "Guild not found.")

    players.sort(key=lambda x: x['name'])

    resp = {
        "name": channel.name,
        "players": players
    }

    return await apcom.prepare_resp(resp)


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


@apcom.kyk.route("/guilds/([^/]+)/channels/([^/]+)/users/([^/]+)/?")  # /guilds/server_id/channels/channel_id/users/user_id
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
