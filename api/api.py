# -*- coding:Utf-8 -*-
# !/usr/bin/env python3.5

"""

"""

############
#
#   GUILDS
#
############

# TODO: vérifier la validité des serv/chan ids à chaque fois
import json

from kyoukai import Kyoukai, HTTPRequestContext
from discord.enums import ChannelType
from collections import defaultdict
from cogs.utils import commons, prefs, scores, checks

api = Kyoukai('dh_api')

async def prepare_resp(resp_payload, code=200):
    return json.dumps(resp_payload), code, {
        "Content-Type": "application/json"
    }

async def list_members(server_id, channel_id):
    server = commons.bot.get_server(server_id)

    if server:
        channel = server.get_channel(channel_id)
        if channel:
            activated = checks.is_activated_check(channel)

            if activated or prefs.getPref(server, "global_scores"):
                players = []
                table = scores.getChannelPlayers(channel, columns=['shoots_fired'])

                for member in table:
                    if checks.is_player_check(member):
                        try:
                            player = server.get_member(member['id_'])

                            players.append({
                                "id": player.id,
                                "name": player.display_name,
                                "avatar": player.avatar_url.replace('.webp', '.png') or player.default_avatar_url # Tempfix pour le png
                            })
                        except:
                            pass
            else:
                return None # Channel not activated
        else:
            return None # Channel not found
    else:
        return None # Guild not found

    players.sort(key=lambda x: x['name'])

    data = {
        "server": server,
        "channel": channel,
        "players": players
    }

    return data

def check_int(func):
    def wrapper(**kwargs):
        return func({k: (v if isinstance(v, HTTPRequestContext) else int(v)) for (k, v) in kwargs})
    return wrapper

@api.route("/guilds/?")
async def guilds(ctx: HTTPRequestContext):
    await commons.bot.wait_until_ready()

    servers = []
    server_count = 0

    for server in commons.bot.servers:
        global_scores = prefs.getPref(server, "global_scores")
        channel_count = 0
        hasPlayers = False

        for channel in server.channels:
            activated = checks.is_activated_check(channel)
            if activated and channel.type == ChannelType.text:
                channel_count += 1
                if not hasPlayers:
                    table = scores.getChannelPlayers(channel, columns=['shoots_fired'])
                    for member in table:
                        if checks.is_player_check(member):
                            hasPlayers = True
                            break

        if channel_count > 0 and hasPlayers:
            server_count += 1
            servers.append({
                                "id": server.id,
                                "name": server.name,
                                "icon": server.icon_url or 'https://placeholdit.imgix.net/~text?txtsize=64&txt={}&w=128&h=128'.format(server.name[0])
                            })

    servers.sort(key=lambda x: x['name'])

    resp = {
        "servers": servers,
        "server_count": server_count
    }

    return await prepare_resp(resp)

@check_int
@api.route("/guilds/([^/]+)/?")  # /guilds/server_id
async def guild(ctx: HTTPRequestContext, server_id: int):
    await commons.bot.wait_until_ready()

    server = commons.bot.get_server(server_id)

    if server:
        player_count = 0
        channels = []

        global_scores = prefs.getPref(server, "global_scores")

        stats = defaultdict(int)

        if not global_scores:
            for channel in server.channels:
                activated = checks.is_activated_check(channel)
                if activated and channel.type == ChannelType.text:
                    table = scores.getChannelPlayers(channel, columns=['shoots_fired'])
                    for member in table:
                        if checks.is_player_check(member):
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
            data = await list_members(server_id, server_id)

            if data:
                resp = {
                    "server": {"id": data['server'].id, "name": data['server'].name},
                    "players": data['players'],
                    "global_scores": global_scores
                }
            else:
                return await prepare_resp(None, 404) # Error

        return await prepare_resp(resp)
    else:
        return await prepare_resp(None, 404) # Guild not found


@check_int
@api.route("/guilds/([^/]+)/channels/([^/]+)/?")  # /guilds/server_id/channels/channel_id
async def guild_channel(ctx: HTTPRequestContext, server_id: int, channel_id: int):
    await commons.bot.wait_until_ready()

    data = await list_members(server_id, channel_id)

    if data:
        resp = {
            "name": data['channel'].name,
            "players": data['players']
        }
    else:
        return await prepare_resp(None, 404) # Error

    return await prepare_resp(resp)


@check_int
@api.route("/guilds/([^/]+)/channels/([^/]+)/users/([^/]+)/?")  # /guilds/server_id/channels/channel_id/users/user_id
async def guild_channel_user(ctx: HTTPRequestContext, server_id: int, channel_id: int, user_id: int):

    await commons.bot.wait_until_ready()
    server = commons.bot.get_server(server_id)

    if server:
        channel = server.get_channel(channel_id)
        if channel:
            activated = checks.is_activated_check(channel)
            if activated:
                player = server.get_member(user_id)

                resp = scores.getChannelPlayers(channel, match_id=user_id)[0]
                resp['avatar'] = player.avatar_url.replace('.webp', '.png') or player.default_avatar_url
            else:
                return await prepare_resp(None, 404) # Channel not activated
        else:
            return await prepare_resp(None, 404) # Channel not found
    else:
        return await prepare_resp(None, 404) # Guild not found

    return await prepare_resp(resp)


############
#
#   stats
#
############


@api.route("/stats/messages_recived/?")
async def messages_recived(ctx: HTTPRequestContext):
    resp = commons.number_messages
    return await prepare_resp(resp)


@api.root.errorhandler(500)
async def handle_500(ctx: HTTPRequestContext, exception_to_handle: Exception):
    return repr(exception_to_handle)
