import datetime
import os
import re
import sys

import discord
import psutil
from discord.ext import commands

from cogs.utils import comm, commons
from cogs.utils.commons import _
from cogs.utils.prefs import getPref
from .utils import checks


class TimeParser:
    def __init__(self, argument):
        compiled = re.compile(r"(?:(?P<hours>\d+)h)?(?:(?P<minutes>\d+)m)?(?:(?P<seconds>\d+)s)?")
        self.original = argument
        try:
            self.seconds = int(argument)
        except ValueError as e:
            match = compiled.match(argument)
            if match is None or not match.group(0):
                raise commands.BadArgument('Failed to parse time.') from e

            self.seconds = 0
            hours = match.group('hours')
            if hours is not None:
                self.seconds += int(hours) * 3600
            minutes = match.group('minutes')
            if minutes is not None:
                self.seconds += int(minutes) * 60
            seconds = match.group('seconds')
            if seconds is not None:
                self.seconds += int(seconds)

        if self.seconds < 0:
            raise commands.BadArgument('I don\'t do negative time.')

        if self.seconds > 604800:  # 7 days
            raise commands.BadArgument('That\'s a bit too far in the future for me.')


class Meta:
    """Commands for utilities related to Discord or the Bot itself."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='quit', hidden=True)
    @checks.is_owner()
    async def _quit(self):
        """Quits the bot."""
        # await ducks.allCanardsGo()
        raise KeyboardInterrupt

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

    # @commands.command()
    # async def join(self):
    #     """Joins a server."""
    #     msg = 'It is no longer possible to ask me to join via invite. So use this URL instead.\n\n'
    #     perms = discord.Permissions.none()
    #     perms.read_messages = True
    #     perms.send_messages = True
    #     perms.manage_messages = True
    #     perms.embed_links = True
    #     perms.read_message_history = True
    #     perms.attach_files = True
    #     await self.bot.say(msg + discord.utils.oauth_url(self.bot.client_id, perms))

    # @commands.command(pass_context=True, no_pm=True)
    # @checks.admin_or_permissions(manage_server=True)
    # async def leave(self, ctx):
    #     """Leaves the server.
    #
    #     To use this command you must have Manage Server permissions or have
    #     the Bot Admin role.
    #     """
    #     server = ctx.message.server
    #     try:
    #         await self.bot.leave_server(server)
    #     except:
    #         await self.bot.say('Could not leave..')

    @commands.command()
    async def uptime(self):
        """Tells you how long the bot has been up for."""
        await self.bot.say('Uptime: **{}**'.format(self.get_bot_uptime()))


    @commands.command(rest_is_raw=True, hidden=True)
    @checks.is_owner()
    async def echo(self, *, content):
        await self.bot.say(content)

    @commands.command(hidden=True)
    @checks.is_owner()
    async def commandstats(self):
        msg = 'Since startup, {} commands have been used.\n{}'
        counter = self.bot.commands_used
        await self.bot.say(msg.format(sum(counter.values()), counter))

    @commands.command(pass_context=True)
    async def stats(self, ctx):
        language = getPref(ctx.message.server, "language")
        embed = discord.Embed(description=_("Usage statistics of duckhunt", language))
        embed.title = "DUCKHUNT STATS"
        # embed.set_author(name=str(target), icon_url=target.avatar_url)
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        embed.url = 'https://api-d.com/duckhunt/'
        compteurCanards = 0
        serveurs = 0
        channels = 0
        membres = 0
        servsFr = 0
        servsEn = 0
        servsEt = 0
        servsDon = 0
        p100cj = 0
        p50cj = 0
        p24cj = 0
        m24cj = 0
        for server in self.bot.servers:
            serveurs += 1
            slang = getPref(server, "language")
            if slang == "fr_FR":
                servsFr += 1
            elif slang == "en_EN":
                servsEn += 1
            else:
                commons.logger.debug("Serveur étranger : {lang : " + str(slang) + ", server:" + str(server.name) + "|" + str(server.id) + "}")
                servsEt += 1
            if getPref(server, "user_can_give_exp"):
                servsDon += 1
            cj = getPref(server, "ducks_per_day")
            if cj is not None:
                if cj >= 100:
                    p100cj += 1
                    p50cj += 1
                    p24cj += 1
                elif cj >= 50:
                    p50cj += 1
                    p24cj += 1
                elif cj > 24:
                    p24cj += 1
                elif cj < 24:
                    m24cj += 1

            for channel in server.channels:
                channels += 1
                if channel in commons.ducks_planned.keys():
                    compteurCanards += commons.ducks_planned[channel]
            membres += len(server.members)
        pid = os.getpid()
        py = psutil.Process(pid)
        memoryUsed = py.memory_info()[0] / 2. ** 30
        now = datetime.datetime.utcnow()
        delta = now - self.bot.uptime
        uptime = delta.total_seconds()

        embed.add_field(name=_("Number of activated channels", language), value=str(len(commons.ducks_planned)))
        embed.add_field(name=_("Number of servers", language), value=str(serveurs))
        embed.add_field(name=_("Number of french servers", language), value=str(servsFr))
        embed.add_field(name=_("Number of english servers", language), value=str(servsEn))
        embed.add_field(name=_("Number of servers with another language setup", language), value=str(servsEt))
        embed.add_field(name=_("Number of channels", language), value=str(channels))
        embed.add_field(name=_("Number of users", language), value=str(membres))
        embed.add_field(name=_("Number of ducks", language), value=str(compteurCanards))
        embed.add_field(name=_("Number of ducks per minute", language), value=str(round(compteurCanards / 1440, 4)))
        embed.add_field(name=_("Number of messages recived", language), value=str(commons.number_messages))
        embed.add_field(name=_("Number of commands recived", language), value=str(sum(self.bot.commands_used.values())))
        embed.add_field(name=_("Number of commands per minute", language), value=str(round(sum(self.bot.commands_used.values()) / (uptime / 60), 4)))
        embed.add_field(name=_("Number of messages per minute", language), value=str(round(commons.number_messages / (uptime / 60), 4), ))
        embed.add_field(name=_("Uptime in seconds", language), value=str(uptime))
        embed.add_field(name=_("Uptime in hours", language), value=str(int(uptime / 60 / 60)))
        embed.add_field(name=_("Uptime in days", language), value=str(int(uptime / 60 / 60 / 24)))
        embed.add_field(name=_("Servers with send exp activated", language), value=str(servsDon))
        embed.add_field(name=_("Servers with more than 100 ducks per day", language), value=str(p100cj))
        embed.add_field(name=_("Servers with more than 50 ducks per day", language), value=str(p50cj))
        embed.add_field(name=_("Servers with more than 24 ducks per day", language), value=str(p24cj))
        embed.add_field(name=_("Servers with less than 24 ducks per day", language), value=str(m24cj))
        embed.add_field(name=_("Memory used (MB)", language), value=str(round(memoryUsed * 1000, 5)))
        embed.set_footer(text=_('Python version : ', language) + str(sys.version), icon_url='http://cloudpassage.github.io/halo-toolbox/images/python_icon.png')

        try:
            await self.bot.say(embed=embed)
        except:
            commons.logger.exception("error sending embed, with embed " + str(embed.to_dict()))
            await comm.message_user(ctx.message, _(":warning: Error sending embed, check if the bot have the permission embed_links and try again !", language))

    @commands.command(pass_context=True)
    async def ping(self, ctx):
        await comm.message_user(ctx.message, _("BANG OR BANG, what's the best ? :p Anyway I'm up and running", getPref(ctx.message.server, "language")))

    @commands.command(pass_context=True)
    async def wiki(self, ctx):
        await comm.message_user(ctx.message, "https://api-d.com/")

    @commands.command(pass_context=True)
    async def help(self, ctx):
        await comm.message_user(ctx.message, _("Check out our new website ! http://api-d.com/command-list.html", getPref(ctx.message.server, "language")))

def setup(bot):
    bot.add_cog(Meta(bot))
