# -*- coding: utf-8 -*-
import datetime
import time
from discord.ext import commands
import discord

from cogs.helpers import checks

class Meta:
    """Commands for utilities related to Discord or the Bot itself."""

    def __init__(self, bot):
        self.bot = bot
        bot.remove_command("help")

    def get_bot_uptime(self):
        now = datetime.datetime.utcnow()
        delta = now - self.bot.uptime
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        if days:
            fmt = '{d} days, {h} hours, {m} minutes, and {s} seconds'
        else:
            fmt = '{h} hours, {m} minutes, and {s} seconds'

        return fmt.format(d=days, h=hours, m=minutes, s=seconds)

    @commands.command()
    @checks.is_channel_enabled()
    async def uptime(self, ctx):
        """Tells you how long the bot has been up for."""
        _ = self.bot._; language = await self.bot.db.get_pref(ctx.guild, "language")
        await self.bot.send_message(ctx=ctx, message='Uptime: **{}**'.format(self.get_bot_uptime()))
        await self.bot.hint(ctx=ctx, message=_("The bot frequently reboots for updates. Don't worry, it has a 99.8% of uptime.", language))

    @checks.is_server_admin()
    @commands.command(rest_is_raw=True, hidden=True, aliases=["say"])
    async def echo(self, ctx, *, content):
        await self.bot.send_message(ctx=ctx, message=content)

    @checks.is_server_admin()
    @commands.command(rest_is_raw=True, hidden=True, aliases=["say_nomention"])
    async def echo_nomention(self, ctx, *, content):
        try:
            await ctx.message.delete()
        except:
            pass
        await self.bot.send_message(ctx=ctx, message=content, mention=False)

    @commands.command(hidden=True)
    async def commandstats(self, ctx):
        msg = 'Since startup, {} commands have been used.\n{}'
        counter = self.bot.commands_used
        await self.bot.send_message(ctx=ctx, message=msg.format(sum(counter.values()), counter))

    @commands.command()
    async def wiki(self, ctx):
        await self.bot.send_message(ctx=ctx, message="https://duckhunt.me/")

    @commands.command()
    async def help(self, ctx):
        _ = self.bot._; language = await self.bot.db.get_pref(ctx.guild, "language")
        await self.bot.send_message(ctx=ctx, message=_("Here is the command list: http://duckhunt.me/command-list/ | If you need anything, feel free to join the "
                                                       "support server at https://discordapp.com/invite/2BksEkV", language))

    @commands.command(aliases=["date"])
    async def time(self, ctx):
        _ = self.bot._; language = await self.bot.db.get_pref(ctx.guild, "language")
        time_data = int(time.time()) % 86400
        hour = str(int(time_data / 60 / 60)).rjust(2, "0")
        minutes = str(int(time_data / 60 % 60)).rjust(2, "0")
        seconds = str(int(time_data % 60)).rjust(2, "0")

        await self.bot.send_message(ctx=ctx, message=_("It's `{hour}:{minutes}:{seconds}` in the GMT timezone (also known as UTC±00:00), which is the one used by the bot. \nYou can use this website to compare it to yours: https://time.is/compare/GMT", language).format(hour=hour, minutes=minutes, seconds=seconds))
        await self.bot.hint(ctx=ctx, message=_("You can use the `dh!freetime` command to see when you'll get your weapons back for free", language))

    @commands.command()
    @checks.is_channel_enabled()
    async def freetime(self, ctx):
        HOUR = 3600
        DAY = 86400
        _ = self.bot._; language = await self.bot.db.get_pref(ctx.guild, "language")
        now = int(time.time())
        thisDay = now - (now % DAY)
        seconds_left = DAY - (now - thisDay)
        hours = int(seconds_left / HOUR)
        minutes = int((seconds_left - (HOUR * hours)) / 60)
        await self.bot.send_message(ctx=ctx, message=_(":alarm_clock: Next giveback of weapons and magazines in {sec} seconds ({hours} hours and {minutes} minutes).",
                                                       language).format(sec=seconds_left, hours=hours, minutes=minutes))
        await self.bot.hint(ctx=ctx, message=_("A giveback tops up your magazines and gives you your weapon back for free (if confiscated), but it doesn't affect the bullets in your current magazine. "
                                               "If you can, reload beforehand!", language))

    @commands.command()
    async def ping(self, ctx):
        resp = await ctx.send('Pong! Loading...')
        diff = resp.created_at - ctx.message.created_at
        await resp.edit(content=f'Pong! That took {1000*diff.total_seconds():.1f}ms.')

    @commands.command()
    async def shard(self, ctx):
        _ = self.bot._; language = await self.bot.db.get_pref(ctx.guild, "language")
        await self.bot.send_message(ctx=ctx, message=_("You are using shard number {shard} out of {total} total shards", language).format(shard=ctx.guild.shard_id, total=len(self.bot.shards)))


def setup(bot):
    bot.add_cog(Meta(bot))
