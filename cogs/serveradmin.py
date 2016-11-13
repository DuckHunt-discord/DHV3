# -*- coding:Utf-8 -*-
# !/usr/bin/env python3.5

import time

import discord
from discord.ext import commands

from cogs.utils import comm, commons, prefs, scores
from cogs.utils.commons import _
from .utils import checks


class ServerAdmin:
    """Admin-only commands that make the bot dynamic."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    @checks.is_admin()
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
    async def game_ban(self, ctx, member: discord.Member):
        """!game_ban [member]
        Ban someone from the bot on the current channel"""
        scores.setStat(ctx.message.channel, member, "banned", True)
        await comm.message_user(ctx.message, ":ok: Done, user banned :gun:")

    @commands.command(pass_context=True)
    @checks.is_admin()
    async def game_unban(self, ctx, member: discord.Member):
        """!game_unban [member]
        Unban someone from the bot on the current channel"""
        scores.setStat(ctx.message.channel, member, "banned", False)
        await comm.message_user(ctx.message, ":ok: Done, user unbanned :eyes:")

    @commands.command(pass_context=True)
    @checks.is_admin()
    async def give_exp(self, ctx, target: discord.Member, exp: int):
        """!give_exp [target] [exp]
        Require admin powers"""
        scores.addToStat(ctx.message.channel, target, "exp", exp)
        await comm.logwithinfos_ctx(ctx, "[giveexp] Giving " + str(exp) + " exp points to " + target.mention)
        await comm.message_user(ctx.message, _(":ok:, he now have {newexp} exp points !", prefs.getPref(ctx.message.server, "language")).format(
                **{
                    "newexp": scores.getStat(ctx.message.channel, target, "exp")
                    }))

    @commands.command(pass_context=True)
    @checks.is_admin()
    async def duckplanning(self, ctx):
        raise NotImplementedError

    @commands.command(pass_context=True)
    @checks.is_admin()
    async def add_Channel(self, ctx):
        raise NotImplementedError

    @commands.command(pass_context=True)
    @checks.is_admin()
    async def del_channel(self, ctx):
        raise NotImplementedError

    @commands.command(pass_context=True)
    @checks.is_admin()
    async def add_admin(self, ctx, target: discord.Member):
        raise NotImplementedError

    @commands.command(pass_context=True)
    @checks.is_admin()
    async def del_admin(self, ctx, target: discord.Member):
        raise NotImplementedError

    @commands.command(pass_context=True)
    async def claimserver(self, ctx):
        raise NotImplementedError

    @commands.command(pass_context=True)
    @checks.is_admin()
    async def permissions(self, ctx):
        raise NotImplementedError

    @commands.command(pass_context=True)
    @checks.is_admin()
    async def deleteeverysinglescoreandstatonthischannel(self, ctx):
        raise NotImplementedError


    ### SETTINGS ###

    @commands.group(pass_context=True)
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
