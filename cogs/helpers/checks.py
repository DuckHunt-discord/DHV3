import aiohttp
import time
from discord.ext import commands


def is_ready():
    async def predicate(ctx):
        await ctx.bot.wait_until_ready()
        return True

    return commands.check(predicate)


class NotSuperAdmin(commands.CheckFailure):
    pass


def is_super_admin():
    async def predicate(ctx):
        # await ctx.bot.wait_until_ready()
        cond = ctx.message.author.id in ctx.bot.admins
        ctx.logger.debug(f"Check for super-admin returned {cond}")
        if cond:
            return True
        else:
            raise NotSuperAdmin

    return commands.check(predicate)


class NotServerAdmin(commands.CheckFailure):
    pass


def is_server_admin():
    async def predicate(ctx):
        # await ctx.bot.wait_until_ready()
        cond = ctx.message.author.id in ctx.bot.admins  # User is super admin
        cond = cond or ctx.message.channel.permissions_for(ctx.message.author).administrator  # User have server administrator permission
        cond = cond or ctx.message.author.id in await ctx.bot.db.get_admins(ctx.guild)  # User is admin as defined in the database
        ctx.logger.debug(f"Check for admin returned {cond}")

        if cond:
            return True
        else:
            raise NotServerAdmin

    return commands.check(predicate)


def is_channel_enabled():
    async def predicate(ctx):
        # await ctx.bot.wait_until_ready()
        cond = await ctx.bot.db.channel_is_enabled(ctx.channel)  # Coroutine
        ctx.logger.debug(f"Check for channel enabled returned {cond}")
        return cond

    return commands.check(predicate)


def had_giveback():
    async def predicate(ctx):
        # await ctx.bot.wait_until_ready()

        channel = ctx.message.channel
        player = ctx.message.author
        if await ctx.bot.db.get_stat(channel, player, "banned"):
            cond = ctx.message.author.id in ctx.bot.admins  # User is super admin
            cond = cond or ctx.message.channel.permissions_for(ctx.message.author).administrator  # User have server administrator permission
            cond = cond or ctx.message.author.id in await ctx.bot.db.get_admins(ctx.guild)  # User is admin as defined in the database
            if not cond:  # Not even an admin so
                ctx.logger.debug("Banned player trying to play :(")
                return False

        lastGB = int(await ctx.bot.db.get_stat(channel, player, "lastGiveback"))
        if int(lastGB / 86400) != int(int(time.time()) / 86400):
            daygb = int(lastGB / 86400)
            daynow = int(int(time.time()) / 86400)
            ctx.logger.debug(f"Giveback needed : Last GiveBack was on day {daygb}, and we are now on day {daynow}.")
            await ctx.bot.db.giveback(channel=channel, user=player)

        return True

    return commands.check(predicate)


class NotEnoughExp(commands.CheckFailure):
    pass


def have_exp(exp_needed):
    async def predicate(ctx):
        # await ctx.bot.wait_until_ready()
        channel = ctx.message.channel
        player = ctx.message.author
        exp = int(await ctx.bot.db.get_stat(channel, player, "exp"))

        cond = exp >= exp_needed

        if cond:
            return True
        else:
            raise NotEnoughExp

    return commands.check(predicate)


DISCORD_BOTS_ORG_API = 'https://discordbots.org/api'
session = aiohttp.ClientSession()


class NoVotesOnDBL(commands.CheckFailure):
    pass


def voted_lately():
    async def predicate(ctx):
        player = ctx.message.author

        headers = {'authorization': ctx.bot.discordbots_org_key, 'content-type': 'application/json'}

        url = '{0}/bots/{1.user.id}/check?userId={2.id}'.format(DISCORD_BOTS_ORG_API, ctx.bot, player)
        async with session.get(url, headers=headers) as resp:
            cond = bool((await resp.json())['voted'])

        if cond:
            return True
        else:
            raise NoVotesOnDBL

    return commands.check(predicate)
