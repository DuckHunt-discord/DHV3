import copy
import inspect

from discord.ext import commands

from cogs.utils import comm, commons, prefs
from cogs.utils.commons import _
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

    @commands.command()
    @checks.is_owner()
    async def serverlist(self, prefs: str = ""):
        raise NotImplementedError

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
