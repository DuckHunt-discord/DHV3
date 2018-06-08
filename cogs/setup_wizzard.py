import discord
from discord.ext import commands

from cogs.helpers import checks

class SetupWizzard:
    def __init__(self, bot):
        self.bot = bot

    async def on_guild_join(self, guild: discord.Guild):
        channel: discord.TextChannel
        _ = self.bot._
        language = await self.bot.db.get_pref(guild, "language")

        for channel in guild.channels:
            if isinstance(channel, discord.TextChannel):
                if channel.permissions_for(guild.me).send_messages:
                    channel_used = channel
                    break

        else:
            return  # Nowhere to speak

        await self.bot.send_message(where=channel_used, message=_("Hello!\n "
                                                                  "Thanks for adding me in there! I'm almost ready to start the game!\n "
                                                                  "Could we please go into the channel where you want the game to be ? "
                                                                  "Please invoke me there by using `dh!setup`"
                                                                  "<:event_GuildAdded_01:439550913112309781>", language))

    @commands.command(aliases=["claimserver", "claim_server"])
    @checks.is_server_admin()
    async def setup(self, ctx):
        _ = self.bot._
        language = await self.bot.db.get_pref(ctx.guild, "language")
        await self.bot.send_message(ctx=ctx, message=_("Hello again!\n "
                                                       "I'm just gonna run a quick permissions check and will be back in a few seconds! "
                                                       "Please wait", language))

        channel = ctx.channel
        me = ctx.guild.me
        permissions: discord.Permissions
        permissions = channel.permissions_for(me)
        if not permissions.send_messages:
            return  # Can't do anything anyway

        # Bad



        if not permissions.read_message_history:
            await self.bot.send_message(ctx=ctx, message=_(":small_red_triangle: The permission `read_message_history` is missing.\n"
                                                           "This is essential for the normal function of the bot, as I need to be able to read messages.\n"
                                                           "You can proceed without it, but shouldn't.", language))

        if not permissions.add_reactions:
            await self.bot.send_message(ctx=ctx, message=_(":small_red_triangle: The permission `add_reactions` is missing.\n"
                                                           "It's a required permission for interactive embeds, and they are almost everywhere.\n"
                                                           "You could proceed without it, but it's not recommended and could lead to errors", language))

        if not permissions.attach_files:
            await self.bot.send_message(ctx=ctx, message=_(":small_red_triangle: The permission `attach_files` is missing.\n"
                                                           "It's a required permission for embeds, and they are almost everywhere.\n"
                                                           "You could proceed without it, but it's not recommended and could lead to errors", language))

        if not permissions.embed_links:
            await self.bot.send_message(ctx=ctx, message=_(":small_red_triangle: The permission `embed_links` is missing.\n"
                                                           "This is used to send embeds\n"
                                                           "You could proceed without it, but really shouldn't as it will lead to errors", language))
        # Warnings

        if permissions.administrator:
            await self.bot.send_message(ctx=ctx, message=_(":small_orange_diamond: You gave me the `administrator` permission.\n"
                                                           "Although this will not cause problems, it's unsafe to give bots such powerful permissions, especially if they don't need them.\n"
                                                           "You can proceed with it.", language))

        if not permissions.create_instant_invite:
            await self.bot.send_message(ctx=ctx, message=_(":small_orange_diamond: The permission `create_instant_invite` is missing.\n"
                                                           "It's not really essential for the normal function of the bot, but needed for error reports.\n"
                                                           "You can proceed without it.", language))

        if not permissions.manage_messages:
            await self.bot.send_message(ctx=ctx, message=_(":small_orange_diamond: The permission `manage_messages` is missing.\n"
                                                           "This is used to remove some messages on sneaky commands (weapon sabotage, etc.), and also if you use the `delete_commands` setting\n"
                                                           "You could proceed without it, but it's not recommended and could lead to errors", language))

        if permissions.mention_everyone:
            await self.bot.send_message(ctx=ctx, message=_(":small_orange_diamond: You gave me the `mention_everyone` permission.\n"
                                                           "This not used, but should't be given in case of a bug\n"
                                                           "You could proceed with it safely.", language))

        if not permissions.external_emojis:
            await self.bot.send_message(ctx=ctx, message=_(":small_orange_diamond: The permission `external_emojis` is missing.\n"
                                                           "This is used since DHV3 to add non-standard emojis to messages. You should probably give it to me\n"
                                                           "You could proceed without it, but bug reports would be appreciated.", language))

        # Not bad

        # Can't check connect & speak in channel perms
        #if not permissions.connect:
        #    await self.bot.send_message(ctx=ctx, message=_(":small_blue_diamond: The permission `connect` is missing.\n"
        #                                                   "This is not yet used, but could be in the future. An announcement will be made then.\n"
        #                                                   "You can safely proceed without it.", language))

        #if not permissions.speak:
        #    await self.bot.send_message(ctx=ctx, message=_(":small_blue_diamond: The permission `speak` is missing.\n"
        #                                                   "This is not yet used, but could be in the future. An announcement will be made then.\n"
        #                                                   "You can safely proceed without it.", language))

        if not permissions.change_nickname:
            await self.bot.send_message(ctx=ctx, message=_(":small_blue_diamond: The permission `change_nickname` is missing.\n"
                                                           "This is not yet used, but could be in the future. An announcement will be made then.\n"
                                                           "You can safely proceed without it.", language))

        if not permissions.send_tts_messages:
            await self.bot.send_message(ctx=ctx, message=_(":small_blue_diamond: The permission `send_tts_messages` is missing.\n"
                                                           "This is used in case you want to enable tts ducks..\n"
                                                           "You can safely proceed without it, but the `tts_ducks` setting won't work", language))



        await self.bot.send_message(ctx=ctx, message=_("I'm done! <:cmd_Setup_01:439551472804429836>\n"
                                                       "Any warning has been sent above. I suggest fixing them, then running the command again!\n"
                                                       "If there is none, congrats! You passed the tests brilliantly!\n"
                                                       "If you are ready to continue with the setup, use the command `dh!setup_settings`. If you just want to play, use `dh!add_channel`. Once used, "
                                                       "ducks will spawn automatically.\n"
                                                       "Thanks for flying DucksAir. If you have any question, we are here to help at https://discord.gg/2BksEkV",
                                                       language))

    @commands.command()
    @checks.is_server_admin()
    async def setup_settings(self, ctx):
        _ = self.bot._
        language = await self.bot.db.get_pref(ctx.guild, "language")

        await self.bot.send_message(ctx=ctx, message=_(
            """Hey! Let's configure the server!
I'll give you the most used parameters, and let you change them if you want. Any command written here is optional, and you can start playing now just by using `dh!add_channel`.

**Before starting, please make sure this is the channel you want to use, and activate it with `dh!add_channel`.**

**1/ Language used**:
    \* If you speak french, use `dh!settings set language fr_FR`
    \* If you speak spanish, use `dh!settings set language es_ES`
    \* Another language we don't fully support yet? Help us translate DuckHunt! Find us at https://discord.gg/2BksEkV.
    
**2/ Ducks Per Day**:
    This is the number of ducks that will spawn per day. They spawn at random intervals, but you can configure the number of ducks that will spawn.
    \* Use the following command to change it, use `dh!settings set ducks_per_day XX`, where `XX` is a number.
    \* To prevent abuse, there is a limit that will be automatically enforced. If you need to lift it, contact my owner at the support server.
    
**3/ Exp Won Per Duck Killed**:
    This is the experience won per duck killed. If your server is really popular, it might be worth it to push it up a little to make new hunters progress faster.
    \* Use the following command to change it, use `dh!settings set exp_won_per_duck_killed XX`, where `XX` is a number.
    \* :bulb: Don't go too high tho, there must be some challenge. 15 is a good start
    
**4/ Other settings**:
    This is starting to be lengthy, so I won't go into further details here. You are probably all set and can start the game by typing `dh!add_channel`.
    More settings can be found using `dh!settings list`
    
Thanks for playing with me! <:official_Duck_01:439546719177539584>
""", language))





def setup(bot):
    bot.add_cog(SetupWizzard(bot))
