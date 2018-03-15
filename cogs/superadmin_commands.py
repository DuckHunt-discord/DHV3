import inspect
from cogs import spawning
from discord.ext import commands
from cogs.helpers import checks


class SuperAdmin:

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @checks.is_super_admin()
    @checks.is_channel_enabled()
    async def db_id(self, ctx):
        dbid = await self.bot.db.get_channel_dbid(ctx.channel)
        await self.bot.send_message(ctx=ctx, message=f"Channel ID in the DB is {dbid}")

    @commands.command()
    @checks.is_super_admin()
    async def get_level_from_exp(self, ctx, exp: int):
        await self.bot.send_message(ctx=ctx, message=await self.bot.db.get_level(exp))

    @commands.command()
    @checks.is_super_admin()
    async def leave_everywhere(self, ctx):
        for guild in self.bot.guilds:
            if guild != ctx.guild:
                # Dangerous command
                # await guild.leave()
                ctx.logger.info(f"I would leave {guild.id}/{guild.name}")

        await self.bot.send_message(ctx=ctx, message="Check console")

    @commands.command()
    @checks.is_super_admin()
    async def debug(self, ctx, *, code: str):
        """Evaluates code."""
        code = code.strip('` ')
        python = '```py\n{}\n```'
        result = None

        env = {'bot': self.bot, 'ctx': ctx, 'message': ctx.message, 'guild': ctx.message.guild, 'channel': ctx.message.channel, 'author': ctx.message.author}

        env.update(globals())

        try:
            result = eval(code, env)
            if inspect.isawaitable(result):
                result = await result
        except Exception as e:
            await ctx.send(python.format(type(e).__name__ + ': ' + str(e)))
            return

        await self.bot.send_message(ctx=ctx, message=python.format(result))

    @commands.command(aliases=["gen_event", "event_gen"])
    @checks.is_super_admin()
    async def regen_event(self, ctx, force: bool = True):
        """!regen_event"""
        await spawning.event_gen(ctx.bot, force)
        await self.bot.send_message(ctx=ctx, message=":ok_hand: Next event regenerated")

    @commands.command(aliases=["quit", "stop"])
    @checks.is_super_admin()
    async def exit(self, ctx, ):
        """!regen_event"""
        raise KeyboardInterrupt("Exited with command")

    @commands.command(pass_context=True)
    @checks.is_super_admin()
    async def broadcast(self, ctx, *, bc: str):
        """!broadcast [message]"""
        await self.bot.send_message(ctx=ctx, message="Starting the broadcast...")
        ctx.logger.warning(f"Starting broadcast with message : \n{bc}")
        for channel in list(self.bot.ducks_planning.keys()):
            try:
                await self.bot.send_message(where=channel, message=bc, can_pm=False, mention=False)
            except Exception as e:
                ctx.logger.info(f"Error broadcasting to {channel.name} : {e}")
                pass

        ctx.logger.info("Broadcast done.")
        await self.bot.send_message(ctx=ctx, message="Broadcast finished!", return_message=True)  # Rate limits


def setup(bot):
    bot.add_cog(SuperAdmin(bot))
