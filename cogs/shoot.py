from discord.ext import commands

from cogs.utils import comm
from .utils import checks


# to expose to the eval command


class Shoot:
    """Basic commands for shooting and reloading a weapon"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    @checks.is_owner()
    async def kill(self, ctx):
        await comm.logwithinfos_ctx(ctx, "test")
        await self.bot.say("Prout")

    @commands.command(pass_context=True)
    async def bang(self, ctx):
        raise NotImplementedError

    @commands.command(pass_context=True)
    async def reload(self, ctx):
        raise NotImplementedError


def setup(bot):
    bot.add_cog(Shoot(bot))
