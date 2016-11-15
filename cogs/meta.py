import datetime
import os
import re
import sys

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
                    compteurCanards += len(commons.ducks_planned[channel])
            membres += len(server.members)
        pid = os.getpid()
        py = psutil.Process(pid)
        memoryUsed = py.memory_info()[0] / 2. ** 30
        uptime = self.get_bot_uptime()
        now = datetime.datetime.utcnow()
        delta = now - self.bot.uptime
        uptime = delta.total_seconds()

        await comm.message_user(ctx.message, _("""Statistiques de DuckHunt:

    DuckHunt est actif dans `{nbre_channels_actives}` channels, sur `{nbre_serveurs}` serveurs. Il voit `{nbre_channels}` channels, et plus de `{nbre_utilisateurs}` utilisateurs.
    Dans la planification d'aujourd'hui sont prévus et ont été lancés au total `{nbre_canards}` canards (soit `{nbre_canards_minute}` canards par minute).
    Au total, le bot connait `{nbre_serveurs_francais}` serveurs francais, `{nbre_serveurs_anglais}` serveurs anglais et `{nbre_serveurs_etrangers}` serveurs étrangers.
    Il a reçu au total durant la session `{messages}` message(s) (soit `{messages_minute}` message(s) par minute), dont `{commandes}` commandes (soit `{commandes_minute}` commandes(s) par minute).
    Le bot est lancé depuis `{uptime_sec}` seconde(s), ce qui équivaut à `{uptime_min}` minute(s) ou encore `{uptime_heures}` heure(s), ou, en jours, `{uptime_jours}` jour(s).
    Sur l'ensemble des serveurs, `{servsDon}` ont activé le don d'experience, `{plusde100cj}` serveurs font apparaitre plus de 100 canards par jour, `{plusde24cj}` serveurs en font plus de 24 par jours, tandis que `{moinsde24cj}` en font apparaitre moins de 24 par jour!
    Le bot utilise actuellement `{memory_used}` MB de ram.

    Le bot est lancé avec Python ```{python_version}```""", language).format(**{
            "nbre_channels_actives"  : len(commons.ducks_planned),
            "nbre_serveurs"          : serveurs,
            "nbre_serveurs_francais" : servsFr,
            "nbre_serveurs_anglais"  : servsEn,
            "nbre_serveurs_etrangers": servsEt,
            "nbre_channels"          : channels,
            "nbre_utilisateurs"      : membres,
            "nbre_canards"           : compteurCanards,
            "nbre_canards_minute"    : round(compteurCanards / 1440, 4),
            "messages"               : commons.number_messages,
            "commandes"              : sum(self.bot.commands_used.values()),
            "messages_minute"        : round(commons.number_messages / (uptime / 60), 4),
            "commandes_minute"       : round(sum(self.bot.commands_used.values()) / (uptime / 60), 4),
            "uptime_sec"             : uptime,
            "uptime_min"             : int(uptime / 60),
            "uptime_heures"          : int(uptime / 60 / 60),
            "uptime_jours"           : int(uptime / 60 / 60 / 24),
            "servsDon"               : servsDon,
            "plusde100cj"            : p100cj,
            "plusde50cj"             : p50cj,  # NU
            "plusde24cj"             : p24cj,
            "moinsde24cj"            : m24cj,
            "memory_used"            : round(memoryUsed * 1000, 5),
            "python_version"         : str(sys.version)
        }))

    @commands.command(pass_context=True)
    async def ping(self, ctx):
        await comm.message_user(ctx.message, "BANG OR BANG, what's the best ? :p Anyway I'm up and running")

    @commands.command(pass_context=True)
    async def wiki(self, ctx):
        await comm.message_user(ctx.message, "https://api-d.com/duckhunt/index.php/")


def setup(bot):
    bot.add_cog(Meta(bot))
