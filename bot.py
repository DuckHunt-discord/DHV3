#!/usr/bin/env python3.6
# This is DuckHunt V3
# You have to use it with the rewrite version of discord.py
# You can install it using
# pip install -U git+https://github.com/Rapptz/discord.py@rewrite#egg=discord.py[voice]
# You also have to use python 3.6 to run this
# Have fun !
# The doc for d.py rewrite is here : http://discordpy.readthedocs.io/en/rewrite/index.html


# Installation tutorial : https://kb.api-d.com/en/code/duckhunt-how-to/
# Support server : https://discord.gg/G4skWae


# Importing and creating a logger

import logging
import traceback

import time
from typing import Union

import cogs.helpers.aux_inits as inits
from cogs.helpers import checks
from cogs.helpers.context import CustomContext

base_logger = inits.init_logger()

extra = {"channelid": 0, "userid": 0}
logger = logging.LoggerAdapter(base_logger, extra)

logger.info("Starting the bot")

# Setting up asyncio to use uvloop if possible, a faster implementation on the event loop
import asyncio

try:
    import uvloop
except ImportError:
    logger.warning("Using the not-so-fast default asyncio event loop. Consider installing uvloop.")
    pass
else:
    logger.info("Using the fast uvloop asyncio event loop")
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

# Importing the discord API warpper
import discord
import discord.ext.commands as commands


# Prepare the bot object

async def get_prefix(bot, message):
    extras = [await bot.db.get_pref(message.guild, "prefix"), "duckhunt", "dh!", "dh", "Dh", "Dh!", "dH!", "dH", "DH!", "DH"]
    return commands.when_mentioned_or(*extras)(bot, message)


logger.debug("Creating a bot instance of commands.AutoShardedBot")

from cogs.helpers import context


class DuckHunt(commands.AutoShardedBot):
    async def on_message(self, message):
        if message.author.bot:
            return  # ignore messages from other bots

        if message.author.id in self.blacklisted_users:
            return

        if message.guild is None:  # Private message
            return

        ctx = await self.get_context(message, cls=context.CustomContext)
        if ctx.prefix is not None:
            # ctx.command = self.all_commands.get(ctx.invoked_with.lower())  # This dosen't works for subcommands
            await self.invoke(ctx)

    async def on_command(self, ctx):
        bot.commands_used[ctx.command.name] += 1
        ctx.logger.info(f"<{ctx.command}> {ctx.message.clean_content}")
        if await self.db.get_pref(ctx.guild, "delete_commands"):
            await ctx.message.delete()

    async def on_ready(self):
        logger.info("We are all set, on_ready was fired! Yeah!")
        logger.info(f"I see {len(self.guilds)} guilds")
        await self.log(level=30, title="Bot is ready", message=f"The bot has restarted. We can now see {len(self.guilds)} guilds on {self.shard_count} shards, and ducks can now spawn", where=None)

    async def log_guild_stats(self, e, guild):
        e.add_field(name='Name', value=guild.name)
        e.add_field(name='ID', value=guild.id)
        e.add_field(name='Owner', value=f'{guild.owner} (ID: {guild.owner.id})')

        bots = sum(m.bot for m in guild.members)
        total = guild.member_count
        online = sum(m.status is discord.Status.online for m in guild.members)
        e.add_field(name='Members', value=str(total))
        e.add_field(name='Bots', value=f'{bots} ({bots/total:.2%})')
        e.add_field(name='Online', value=f'{online} ({online/total:.2%})')

        if guild.icon:
            e.set_thumbnail(url=guild.icon_url)

        if guild.me:
            e.timestamp = guild.me.joined_at

        await self.send_message(where=self.get_channel(self.log_channel_id), embed=e, mention=False, can_pm=False)

    async def on_guild_join(self, guild):
        e = discord.Embed(colour=0x53dda4, title='New Guild')  # green colour
        await self.log_guild_stats(e, guild)

    # await self.log(level=6, title="Joined Guild", message=f"Yay! A new server! Current guild total : {len(self.guilds)}", where=guild)

    async def on_guild_remove(self, guild):
        e = discord.Embed(colour=0xdd5f53, title='Left Guild')  # red colour
        await self.log_guild_stats(e, guild)

        # await self.log(level=6, title="Left Guild", message=f"Goodbye! Current guild total : {len(self.guilds)}", where=guild)
        logger.info(f"Guild removed (from discord) : {guild} :(!")

        for channel in guild.channels:
            self.ducks_planning.pop(channel, None)

        logger.info(f"Before removing ducks, we had {len(bot.ducks_spawned)} ducks")

        self.ducks_spawned = [duck for duck in self.ducks_spawned if duck.channel not in guild.channels]

        logger.info(f"After removing ducks, we have {len(bot.ducks_spawned)} ducks")

    async def on_guild_channel_delete(self, channel):
        logger.info(f"Channel removed (from discord) : {channel} :(!")

        self.ducks_planning.pop(channel, None)
        self.ducks_spawned = [duck for duck in self.ducks_spawned if duck.channel != channel]

    async def on_command_error(self, context, exception):
        _ = self._;
        language = await self.db.get_pref(context.guild, "language")
        if isinstance(exception, discord.ext.commands.errors.CommandNotFound):
            return

        elif isinstance(exception, discord.ext.commands.errors.MissingRequiredArgument):
            await self.send_message(ctx=context, message=_(":x: A required argument is missing.", language))  # Here is the command documentation : \n```\n", language) + context.command.__doc__ +
            # "\n```")
            return
        elif isinstance(exception, checks.NotEnoughExp):
            await self.send_message(ctx=context, message=_(":x: You don't have enough exp for this", language))
            return
        elif isinstance(exception, checks.NotServerAdmin):
            await self.send_message(ctx=context, message=_(":x: You are not a server admin", language))
            return
        elif isinstance(exception, checks.NotSuperAdmin):
            await self.send_message(ctx=context, message=_(":x: You are not a super admin.", language))
            await self.hint(ctx=context, message=_("This command is reserved for the bot owners. "
                                                   "If you think this is an error, please contact my owner at the DuckHunt Support Server (see `dh!help`).", language))
            return
        elif isinstance(exception, checks.NoVotesOnDBL):
            await self.send_message(ctx=context, message=_(":x: You haven't voted for DuckHunt on DiscordBotList for a while.", language))
            await self.hint(ctx=context, message=_("Support the bot to use this command by voting at <https://discordbots.org/bot/duckhunt>. "
                                                   "Be aware that the votes can take a minute to be registered by Duckhunt"
                                                   "If you think this is an error, please contact my owner at the DuckHunt Support Server (see `dh!help`).", language))
            return
        elif isinstance(exception, discord.ext.commands.errors.CheckFailure):
            return
        elif isinstance(exception, discord.ext.commands.errors.CommandOnCooldown):
            if context.message.author.id in self.admins:
                await context.reinvoke()
                return
            else:

                await self.send_message(context, message=_("You are on cooldown :(, try again in {seconds} seconds!", language).format(seconds=round(exception.retry_after, 1)))
                return
        logger.error('Ignoring exception in command {}:'.format(context.command))
        logger.error("".join(traceback.format_exception(type(exception), exception, exception.__traceback__)))

    async def hint(self, ctx, message):
        hint_start = ctx.bot._(":bulb: HINT: ")
        await self.send_message(ctx, message=hint_start + message)

    async def log(self, title: str, message: str, where: Union[CustomContext, discord.TextChannel, discord.Guild, None], level: int):
        if isinstance(where, CustomContext):
            footer = f"On {where.channel.id} (#{where.channel.name}), by {where.author.id} ({where.author.name}#{where.author.discriminator})"
        elif isinstance(where, discord.TextChannel):
            footer = f"On {where.id} (#{where.name})"
        elif isinstance(where, discord.Guild):
            footer = f"On {where.id} (#{where.name})"
        elif where is None:
            footer = ""
        else:
            footer = ""
            logger.warning("Unknown where on logging to a channel : " + str(where))

        embed = discord.Embed(description=message)
        embed.title = title
        embed.set_footer(text=footer)
        if 0 <= level <= 5:
            embed.colour = discord.Colour.green()
        elif 6 <= level <= 10:
            embed.colour = discord.Colour.greyple()
        elif 11 <= level <= 20:
            embed.colour = discord.Colour.orange()
        elif 21 <= level <= 30:
            embed.colour = discord.Colour.red()
        else:
            embed.colour = discord.Colour.dark_red()

        await self.send_message(where=self.get_channel(self.log_channel_id), embed=embed, mention=False, can_pm=False)

    async def send_message(self, ctx: context.CustomContext = None, from_: discord.Member = None, where: discord.TextChannel = None, message: str = "", embed: discord.Embed = None,
                           can_pm: bool = True, force_pm: bool = False, mention=True, try_: int = 1, return_message: bool = False):

        if not return_message:
            async def send_m():
                return await self.send_message(ctx=ctx, from_=from_, where=where, message=message, embed=embed, can_pm=can_pm, force_pm=force_pm, mention=mention, try_=try_, return_message=True)

            return asyncio.ensure_future(send_m())

        s = time.time()

        original_message = message
        if 10000 > len(message) > 1900:
            message = message.split("\n")
            current_message = 0
            to_send = ""
            for line in message:
                line = line + "\n"
                if len(to_send) + len(line) <= 1800:
                    to_send += line
                else:
                    if "```" in to_send:
                        # TODO: Check if number of ``` match.
                        to_send += "```"
                        line = "```" + line

                    await self.send_message(ctx=ctx, from_=from_, where=where, message=to_send, embed=embed, can_pm=can_pm, force_pm=force_pm, mention=False, try_=try_, return_message=True)  #
                    # Return message at true to ensure order
                    to_send = line

            m = await self.send_message(ctx=ctx, from_=from_, where=where, message=to_send, embed=embed, can_pm=can_pm, force_pm=force_pm, mention=False, try_=try_, return_message=True)
            return m

        if ctx:
            from_ = ctx.message.author
            where = ctx.channel
            logger = ctx.logger
        else:
            extra = {"channelid": where.id if where else 0, "userid": from_.id if from_ else 0}
            logger = logging.LoggerAdapter(bot.base_logger, extra)

        # bot.logger.debug(f"Long message took : {time.time() - s}.")

        if where:  # Where is a TextChannel
            if force_pm or (can_pm and await self.db.get_pref(where.guild, "pm_most_messages")):
                if from_:  # If I have someone to PM
                    where = await from_.create_dm()
                    permissions = True
                else:
                    logger.warning(f"I want to PM this message, but I can't since I don't have a from_ User\n"
                                   f"ctx={ctx}, from_={from_}, where={where},\n"
                                   f"message : {message}")
                    permissions = True  # TODO: Check perms

            else:
                permissions = True  # TODO: Check perms
                if mention and from_:
                    message = f"{from_.mention} > {message}"


        else:  # Where will be a DMChannel
            if from_:
                where = await from_.create_dm()
                permissions = True
            else:
                logger.error(f"Can't send the message : don't know where to send it")
                raise TypeError(f"Need a `ctx`, `to` or `where`, but ctx={ctx} | from_={from_} | where={where} given")

        # bot.logger.debug(f"Where took : {time.time() - s}.")

        if not permissions:
            logger.warning("No permissions to speak here")
            return False

        # Where can be a TextChannel or a DMChannel
        # from_ is a Member or None
        # ctx can be a Context or None

        try:
            m = await where.send(message, embed=embed)
            return m
        except discord.errors.Forbidden:
            logger.warning(f"Could not send {message} to channel : no I/O permissions")
            return False
        except discord.errors.NotFound:
            logger.warning(f"Could not send {message} to channel : channel not found.")
            return False
        except Exception as e:
            if try_ >= 3:
                logger.warning(f"Could not send {message} to channel after 3 tries")
                logger.exception("Exception for not sending is :")
                await bot.log(level=15, title="Error when sending message (x3)", message=f"See bot console for exception ({e})", where=ctx)

                return False
            else:
                return await self.send_message(ctx=ctx, from_=from_, where=where, message=original_message, embed=embed, can_pm=can_pm, force_pm=force_pm, mention=mention, try_=try_ + 1,
                                               return_message=return_message)


bot = DuckHunt(command_prefix=get_prefix, case_insensitive=True)

logger.debug("Configuring the bot")

from cogs.helpers.config import config

config(bot)
bot.base_logger = base_logger
bot.logger = logger

logger.debug("Loading the BG loop :")
from cogs import spawning

bot.loop.create_task(spawning.background_loop(bot))

logger.debug("> Loading complete")

logger.debug("Loading cogs : ")

######################
#                 |  #
#   ADD COGS HERE |  #
#                 V  #
#################   ##
#################   ##
################   ###
###############   ####
##############   #####

cogs = ['cogs.admin_commands', 'cogs.analytics', 'cogs.experience_related_commands', 'cogs.helpers.database', 'cogs.meta', 'cogs.scores', 'cogs.setup_wizzard', 'cogs.shop', 'cogs.superadmin_commands',
        'cogs.user_commands', 'cogs.evals', 'cogs.api'  # This must be the last to run, comment if you don't need it
        ]

for extension in cogs:
    try:
        bot.load_extension(extension)
        logger.debug(f"> {extension} loaded!")
    except Exception as e:
        logger.exception('> Failed to load extension {}\n{}: {}'.format(extension, type(e).__name__, e))

logger.debug("Everything seems fine, we are now connecting to discord and entering the mainloop.")
try:
    # bot.loop.set_debug(True)
    bot.loop.run_until_complete(bot.start(bot.token))
except KeyboardInterrupt:
    pass
finally:
    # Stop cleanly : make ducks leave
    # try:
    game = discord.Game(name=f"Restarting...")
    bot.loop.run_until_complete(bot.change_presence(status=discord.Status.dnd, activity=game))
    bot.loop.run_until_complete(spawning.make_all_ducks_leave(bot))

    # except:
    #    pass

    bot.loop.run_until_complete(bot.logout())

    asyncio.sleep(3)
    bot.loop.close()
