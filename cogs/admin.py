import copy
import inspect
import time

from discord.ext import commands
from prettytable import PrettyTable

from cogs.utils import comm, commons, prefs
from cogs.utils.commons import _
from cogs.utils.prefs import JSONloadFromDisk
from .utils import checks


class Admin:
    """Admin-only commands that make the bot dynamic."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    @checks.is_owner()
    async def load(self, *, module: str):
        """Loads a module."""
        try:
            self.bot.load_extension(module)
        except Exception as e:
            await self.bot.say('\N{PISTOL}')
            await self.bot.say('{}: {}'.format(type(e).__name__, e))
        else:
            await self.bot.say('\N{OK HAND SIGN}')

    @commands.command(hidden=True)
    @checks.is_owner()
    async def unload(self, *, module: str):
        """Unloads a module."""
        try:
            self.bot.unload_extension(module)
        except Exception as e:
            await self.bot.say('\N{PISTOL}')
            await self.bot.say('{}: {}'.format(type(e).__name__, e))
        else:
            await self.bot.say('\N{OK HAND SIGN}')

    @commands.command(name='reload_cog', hidden=True)
    @checks.is_owner()
    async def _reload(self, *, module: str):
        """Reloads a module."""
        try:
            self.bot.unload_extension(module)
            self.bot.load_extension(module)
        except Exception as e:
            await self.bot.say('\N{PISTOL}')
            await self.bot.say('{}: {}'.format(type(e).__name__, e))
        else:
            await self.bot.say('\N{OK HAND SIGN}')

    @commands.command(pass_context=True, hidden=True)
    @checks.is_owner()
    async def debug(self, ctx, *, code: str):
        """Evaluates code."""
        code = code.strip('` ')
        python = '```py\n{}\n```'
        result = None

        env = {
            'bot'    : self.bot,
            'ctx'    : ctx,
            'message': ctx.message,
            'server' : ctx.message.server,
            'channel': ctx.message.channel,
            'author' : ctx.message.author
        }

        env.update(globals())

        try:
            result = eval(code, env)
            if inspect.isawaitable(result):
                result = await result
        except Exception as e:
            await self.bot.say(python.format(type(e).__name__ + ': ' + str(e)))
            return

        await self.bot.say(python.format(result))

    @commands.command(pass_context=True, hidden=True)
    @checks.is_owner()
    async def do(self, ctx, times: int, *, command):
        """Repeats a command a specified number of times."""
        msg = copy.copy(ctx.message)
        msg.content = command
        for i in range(times):
            await self.bot.process_commands(msg)

    @commands.command(pass_context=True)
    @checks.is_owner()
    async def serverlist(self, ctx, passed_prefs: str = ""):
        language = prefs.getPref(ctx.message.server, "language")

        x = PrettyTable()
        args_ = passed_prefs.split(" ")
        x._set_field_names([_("Name", language), _("Invitation", language), _("Number of enabled channels", language), _("Number of connected users", language), _("Ducks per day", language), _("Number of unneeded permissions", language), _("Number of needed permissions", language)])
        x.reversesort = True

        tmp = await self.bot.send_message(ctx.message.channel, str(ctx.message.author.mention) + _(" > En cours", language))
        servers = JSONloadFromDisk("channels.json", default="{}")

        total = len(self.bot.servers)
        i = 0
        lu = 0
        for server in self.bot.servers:
            i += 1
            if time.time() - lu >= 1.5 or i == total:
                lu = time.time()
                try:
                    await self.bot.edit_message(tmp, str(ctx.message.author.mention) + _(" > Processing servers ({done}/{total})", language).format(**{
                        "done": i,
                        "total": total
                        }))
                except:
                    pass
            invite = None

            permissionsToHave = ["change_nicknames", "connect", "create_instant_invite", "embed_links", "manage_messages", "mention_everyone", "read_messages", "send_messages", "send_tts_messages"]

            permEnMoins = 0
            permEnPlus = 0
            channel = server.default_channel
            for permission, value in channel.permissions_for(server.me):
                if not value and permission in permissionsToHave:
                    permEnMoins += 1
                elif value and not permission in permissionsToHave:
                    permEnPlus += 1

            if "invitations" in args_:
                for channel in server.channels:
                    permissions = channel.permissions_for(server.me)
                    if permissions.create_instant_invite:
                        try:
                            invite = await self.bot.create_invite(channel, max_age=10 * 60)
                            invite = invite.url
                        except:
                            invite = ""
                    else:
                        invite = ""
            try:
                channels = str(len(servers[server.id]["channels"]))
            except KeyError:  # Pas de channels ou une autre merde dans le genre ?
                channels = "0"

            x.add_row([server.name, invite, channels + "/" + str(len(server.channels)), server.member_count, prefs.getPref(server, "ducks_per_day"), permEnPlus, permEnMoins])

        await comm.message_user(ctx.message, "```\n" + x.get_string(sortby=_("Number of connected users", language)) + "\n```")

    @commands.command(pass_context=True)
    @checks.is_owner()
    async def broadcast(self, ctx, *, bc: str):
        """!broadcast [message]"""
        language = prefs.getPref(ctx.message.server, "language")
        await comm.message_user(ctx.message, _("Starting the broadcast", language))
        await comm.logwithinfos_ctx(ctx, "Broadcast started")
        for channel in commons.ducks_planned.keys():
            try:
                await self.bot.send_message(channel, bc)
            except:
                await comm.logwithinfos_ctx(ctx, "Error broadcasting to " + channel)
                pass
        await comm.logwithinfos_ctx(ctx, "Broadcast ended")
        await comm.message_user(ctx.message, _("Broadcast finished", language))


def setup(bot):
    bot.add_cog(Admin(bot))
