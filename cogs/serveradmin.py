# -*- coding:Utf-8 -*-
# !/usr/bin/env python3.5

import time

import discord
from discord.ext import commands

from cogs.utils import comm, scores
from .utils import checks


class ServerAdmin:
    """Admin-only commands that make the bot dynamic."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    @checks.is_admin()
    async def coin(self, ctx):
        """Spawn a duck on the current channel """
        from cogs.utils.ducks import spawn_duck
        await spawn_duck({
            "channel": ctx.message.channel,
            "time"   : int(time.time())
        })

    @commands.command(pass_context=True)
    @checks.is_admin()
    async def game_ban(self, ctx, member: discord.Member):
        """Ban someone from the bot on the current channel"""
        scores.setStat(ctx.message.channel, member, "banned", True)
        await comm.message_user(ctx.message, ":ok: Done, user banned :gun:")

    @commands.command(pass_context=True)
    @checks.is_admin()
    async def game_unban(self, ctx, member: discord.Member):
        """Unban someone from the bot on the current channel"""
        scores.setStat(ctx.message.channel, member, "banned", False)
        await comm.message_user(ctx.message, ":ok: Done, user unbanned :eyes:")


def setup(bot):
    bot.add_cog(ServerAdmin(bot))
