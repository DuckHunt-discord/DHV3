# -*- coding:Utf-8 -*-
# !/usr/bin/env python3.5

import time

import discord
from discord.ext import commands

from cogs.utils import comm, commons, ducks, prefs, scores
from cogs.utils.commons import _
from .utils import checks


class ServerAdmin:
    """Admin-only commands that make the bot dynamic."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    @checks.is_admin()
    @checks.is_activated_here()
    async def coin(self, ctx):
        """!coin
        Spawn a duck on the current channel """
        from cogs.utils.ducks import spawn_duck
        await spawn_duck({
            "channel": ctx.message.channel,
            "time"   : int(time.time())
        })

    @commands.command(pass_context=True)
    @checks.is_admin()
    @checks.is_activated_here()
    async def game_ban(self, ctx, member: discord.Member):
        """!game_ban [member]
        Ban someone from the bot on the current channel"""
        scores.setStat(ctx.message.channel, member, "banned", True)
        await comm.message_user(ctx.message, ":ok: Done, user banned :gun:")

    @commands.command(pass_context=True)
    @checks.is_admin()
    @checks.is_activated_here()
    async def game_unban(self, ctx, member: discord.Member):
        """!game_unban [member]
        Unban someone from the bot on the current channel"""
        scores.setStat(ctx.message.channel, member, "banned", False)
        await comm.message_user(ctx.message, ":ok: Done, user unbanned :eyes:")

    @commands.command(pass_context=True)
    @checks.is_admin()
    @checks.is_activated_here()
    async def give_exp(self, ctx, target: discord.Member, exp: int):
        """!give_exp [target] [exp]
        Require admin powers"""
        scores.addToStat(ctx.message.channel, target, "exp", exp)
        await comm.logwithinfos_ctx(ctx, "[giveexp] Giving " + str(exp) + " exp points to " + target.mention)
        await comm.message_user(ctx.message, _(":ok:, he now have {newexp} exp points !", prefs.getPref(ctx.message.server, "language")).format(**{
            "newexp": scores.getStat(ctx.message.channel, target, "exp")
        }))

    @commands.command(pass_context=True)
    @checks.is_admin()
    @checks.is_activated_here()
    async def duckplanning(self, ctx):
        table = ""
        for timestamp in commons.ducks_planned[ctx.message.channel]:
            table += str(int((time.time() - timestamp) / 60)) + "\n"

        await self.bot.send_message(ctx.message.author, _(":hammer: TimeDelta in minutes for next ducks\n```{table}```", prefs.getPref(ctx.message.server, "language")).format(**{
            "table": table
        }))

    @commands.command(pass_context=True)
    @checks.is_admin()
    async def add_channel(self, ctx):
        """!del_channel
        Add the current channel to the server
        """
        language = prefs.getPref(ctx.message.server, "language")
        servers = prefs.JSONloadFromDisk("channels.json")

        if not ctx.message.channel.id in servers[ctx.message.server.id]["channels"]:
            await comm.logwithinfos_ctx(ctx, "Adding channel {name} | {id} to channels.json...".format(**{
                "id"  : ctx.message.channel.id,
                "name": ctx.message.channel.name
            }))
            servers[ctx.message.server.id]["channels"].append(ctx.message.channel.id)
            prefs.JSONsaveToDisk(servers, "channels.json")
            await comm.message_user(ctx.message, _(":robot: Channel added !", language))
            await ducks.planifie(ctx.message.channel)
        else:
            await comm.logwithinfos_ctx(ctx, "Channel exists")
            await comm.message_user(ctx.message, _(":x: This channel already exists in the game.", language))

    @commands.command(pass_context=True)
    @checks.is_admin()
    @checks.is_activated_here()
    async def del_channel(self, ctx):
        """!del_channel
        Remove the current channel from the server
        """
        await ducks.del_channel(ctx.message.channel)
        await comm.message_user(ctx.message, ":ok: Channel deleted")

    @commands.command(pass_context=True)
    @checks.is_admin()
    async def add_admin(self, ctx, target: discord.Member):
        """!add_admin [target]
        Remove an admin to the server
        """
        language = prefs.getPref(ctx.message.server, "language")
        servers = prefs.JSONloadFromDisk("channels.json")
        servers[ctx.message.server.id]["admins"] = [target.id]
        await comm.logwithinfos_ctx(ctx, "Adding admin {admin_name} | {admin_id} to configuration file for server {server_name} | {server_id}.".format(**{
            "admin_name" : target.name,
            "admin_id"   : target.id,
            "server_name": ctx.message.server.name,
            "server_id"  : ctx.message.server.id
        }))
        await comm.message_user(ctx.message, _(":robot: OK, {name}  was set as an admin on the server !", language).format(**{
            "name": target.name
        }))

        prefs.JSONsaveToDisk(servers, "channels.json")

    @commands.command(pass_context=True)
    @checks.is_admin()
    async def del_admin(self, ctx, target: discord.Member):
        """!del_admin [target]
        Remove an admin from the server
        """
        language = prefs.getPref(ctx.message.server, "language")
        servers = prefs.JSONloadFromDisk("channels.json")
        if target.id in servers[ctx.message.server.id]["admins"]:
            servers[ctx.message.server.id]["admins"].remove(target.id)
            await comm.logwithinfos_ctx(ctx, "Deleting admin {admin_name} | {admin_id} from configuration file for server {server_name} | {server_id}.".format(**{
                "admin_name" : target.name,
                "admin_id"   : target.id,
                "server_name": ctx.message.server.name,
                "server_id"  : ctx.message.server.id
            }))
            await comm.message_user(ctx.message, _(":robot: OK, {name} was set as an admin on the server !", language).format(**{
                "name": target.name
            }))

            prefs.JSONsaveToDisk(servers, "channels.json")


        else:
            await comm.message_user(ctx.message, _(":robot: OK, {name} is not an admin !", language).format(**{
                "name": target.name
            }))

    @commands.command(pass_context=True)
    async def claimserver(self, ctx):
        """!claimserver
        Sets yourself as an admin if there are no admin configured, IE: when you just added the bot to a server"""
        language = prefs.getPref(ctx.message.server, "language")
        servers = prefs.JSONloadFromDisk("channels.json")
        if not servers[ctx.message.server.id]["admins"]:
            servers[ctx.message.server.id]["admins"] = [ctx.message.author.id]
            await comm.logwithinfos_ctx(ctx, "Adding admin {admin_name} | {admin_id} to configuration file for server {server_name} | {server_id}.".format(**{
                "admin_name" : ctx.message.author.name,
                "admin_id"   : ctx.message.author.id,
                "server_name": ctx.message.server.name,
                "server_id"  : ctx.message.server.id
            }))
            await comm.message_user(ctx.message, _(":robot: OK, you have been set as an admin !", language))
        else:
            await comm.logwithinfos_ctx(ctx, "An admin already exist")
            await comm.message_user(ctx.message, _(":x: An admin exist on this server ! Try !addadmin", language))
        prefs.JSONsaveToDisk(servers, "channels.json")

    @commands.command(pass_context=True)
    @checks.is_admin()
    async def permissions(self, ctx):
        permissionsToHave = ["change_nicknames", "connect", "create_instant_invite", "embed_links", "manage_messages", "mention_everyone", "read_messages", "send_messages", "send_tts_messages"]
        permissions_str = ""
        for permission, value in ctx.message.server.me.permissions_in(ctx.message.channel):
            if value:
                emo = ":white_check_mark:"
            else:
                emo = ":negative_squared_cross_mark:"
            if (value and permission in permissionsToHave) or (not value and not permission in permissionsToHave):
                pass
            else:
                emo += ":warning:"
            permissions_str += "\n{value}\t{name}".format(**{
                "value": emo,
                "name" : str(permission)
                })
        await comm.message_user(ctx.message, _("Permissions : {permissions}", prefs.getPref(ctx.message.server, "language")).format(**{
            "permissions": permissions_str
            }))

    @commands.command(pass_context=True)
    @checks.is_admin()
    @checks.is_activated_here()
    async def deleteeverysinglescoreandstatonthischannel(self, ctx):
        scores.delChannelTable(ctx.message.channel)
        await comm.message_user(ctx.message, _(":ok: Scores / stats of the channel were succesfully deleted.", prefs.getPref(ctx.message.server, "language")))

    ### SETTINGS ###

    @commands.group(pass_context=True)
    @checks.is_activated_here()
    async def settings(self, ctx):
        if not ctx.invoked_subcommand:
            await comm.message_user(ctx.message, "Incorrect syntax : `!settings [view/set/reset/list] [setting if applicable]`")

    @settings.command(pass_context=True, name="view")
    async def view(self, ctx, pref: str):
        """!settings view [pref]"""
        if pref in commons.defaultSettings.keys():
            await comm.message_user(ctx.message, "The setting {pref} is set at {value} on this server.".format(**{
                "value": prefs.getPref(ctx.message.server, pref),
                "pref" : pref
            }))
        else:
            await comm.message_user(ctx.message, ":x: Invalid preference, maybe a typo ? Check the list with `!settings list`")

    @settings.command(pass_context=True, name="set")
    @checks.is_admin()
    async def set(self, ctx, pref: str, value: str):
        """!settings set [pref] [value]
        Admin powers required"""

        if pref in commons.defaultSettings.keys():
            if prefs.setPref(ctx.message.server, pref, value):
                await comm.message_user(ctx.message, ":ok: The setting {pref} was set at `{value}` on this server.".format(**{
                    "value": prefs.getPref(ctx.message.server, pref),
                    "pref" : pref
                }))
            else:
                await comm.message_user(ctx.message, ":x: Incorrect value")
        else:
            await comm.message_user(ctx.message, ":x: Invalid preference, maybe a typo ? Check the list with `!settings list`")

    @settings.command(pass_context=True, name="reset")
    @checks.is_admin()
    async def reset(self, ctx, pref: str):
        """!settings reset [pref]
        Admin powers required"""
        if pref in commons.defaultSettings.keys():
            await prefs.setPref(ctx.message.server, pref)
            await comm.message_user(ctx.message, ":ok: The setting {pref} reset to it's defalut value on this server : `{value}` ".format(**{
                "value": prefs.getPref(ctx.message.server, pref),
                "pref" : pref
            }))
        else:
            await comm.message_user(ctx.message, ":x: Invalid preference, maybe a typo ? Check the list with `!settings list`")

    @settings.command(pass_context=True, name="list")
    async def list(self, ctx):
        """!settings list"""
        await comm.message_user(ctx.message, "List of preferences is available on the wiki : https://api-d.com/duckhunt/index.php/Configuration ")


def setup(bot):
    bot.add_cog(ServerAdmin(bot))
