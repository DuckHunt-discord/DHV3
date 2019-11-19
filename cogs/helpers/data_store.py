from datetime import datetime

import aiohttp

import discord


class Database:
    def __init__(self, bot):
        self.bot = bot
        # Create the database object
        self.url = "https://duckhunt.me/api/"
        self.token = "a8337fb415d6c6543ee69dc53340a28b322c4f66"

        self.headers = {'Authorization': 'Token ' + self.token}
        self.guilds_endpoint = self.url + "guilds/"
        self.channels_endpoint = self.url + "channels/"
        self.gamers_endpoint = self.url + "gamers/"
        self.planning_endpoint = self.url + "planning/"

        self.recreate_caches()

    def recreate_caches(self):
        self._channel_enabled_cache = {}
        self._settings_cache = {}
        self._stats_cache = {}

    async def request_json(self, url):
        self.bot.logger.debug(f"-> {url}")
        headers = self.headers
        async with aiohttp.ClientSession() as cs:
            async with cs.get(url, headers=headers) as r:
                res = await r.json()
                self.bot.logger.debug(f"<- {res[:75]}")
                return res

    async def ensure_guild_exist(self, guild):
        headers = self.headers
        data = {"discord_id": guild.id, "discord_name": guild.name, "discord_created_at": str(guild.created_at), "discord_user_count": guild.member_count}

        self.bot.logger.debug(f"-> Ensure guild exist ({guild.id})")
        async with aiohttp.ClientSession() as cs:
            async with cs.post(self.guilds_endpoint, headers=headers, data=data) as r:
                res = (await r.json())[:75]
                self.bot.logger.debug(f"<- ({r.status}) {res}")

    async def ensure_channel_exist(self, channel):
        headers = self.headers
        data = {"discord_id": channel.id, "discord_name": channel.name}
        await self.ensure_guild_exist(channel.guild)

        self.bot.logger.debug(f"-> Ensure channel exist ({channel.id})")
        async with aiohttp.ClientSession() as cs:
            async with cs.post(self.guilds_endpoint, headers=headers, data=data) as r:
                res = (await r.json())[:75]
                self.bot.logger.debug(f"<- ({r.status}) {res}")

    async def ensure_gamer_exist(self, channel, user):
        headers = self.headers
        data = {"discord_id": user.id, "discord_name": user.name}
        await self.ensure_channel_exist(channel)

        self.bot.logger.debug(f"-> Ensure gamer exist ({channel.id})")
        async with aiohttp.ClientSession() as cs:
            async with cs.post(self.guilds_endpoint, headers=headers, data=data) as r:
                res = (await r.json())[:75]
                self.bot.logger.debug(f"<- ({r.status}) {res}")

    # > Channels <

    # get_pref
    async def channel_is_enabled(self, channel):
        if channel in self._channel_enabled_cache.keys():
            return self._channel_enabled_cache[channel]

        res = await self.get_pref(channel, "enabled")

        self._channel_enabled_cache[channel] = res
        return res

    # set_pref
    async def enable_channel(self, channel):
        await self.set_pref(channel, "enabled", True)
        self._channel_enabled_cache[channel] = True
        await self.bot.log(level=5, title="Channel enabled", message=f"The channel is now active", where=channel)
        if channel in self._stats_cache.keys():
            self._stats_cache[channel] = {}

    # set_pref
    async def disable_channel(self, channel):
        await self.set_pref(channel, "enabled", False)

        self._channel_enabled_cache[channel] = False
        await self.bot.log(level=5, title="Channel disabled", message=f"The channel is now disabled", where=channel)
        if channel in self._stats_cache.keys():
            self._stats_cache[channel] = {}

    # planning
    async def list_enabled_channels(self):
        # [{'guild',guild_id, 'channel': channel_id, 'ducks_per_day': ducks_per_day}, ...]
        return await self.request_json(self.planning_endpoint)

    # > Stats < #

    # get_stat
    async def get_level(self, exp=None, channel=None, player=None):
        levels = self.bot.players_levels

        if not exp:
            exp = await self.get_stat(channel, player, "exp")

        # From https://stackoverflow.com/a/7125547
        # Cherche le "dernier" element de levels qui satifie la condition expMin <= exp

        return next((level for level in reversed(levels) if level["expMin"] <= exp), levels[0])

    # set_stat
    async def giveback(self, channel, user):
        # self.bot.logger.debug(f"> In the DB, the channel is {channel_id}")

        level = await self.get_level(channel=channel, player=user)

        await self.set_stats(channel, user, {"chargeurs": level["chargeurs"], "balles": level["balles"], "lastGiveback": datetime.now()})

        if channel in self._stats_cache.keys():
            if user in self._stats_cache[channel]:
                self._stats_cache[channel].pop(user)
        else:
            self._stats_cache[channel] = {}

    # get_stat
    async def get_stat(self, channel, user, stat: str):
        # self.bot.logger.debug(f"get_stat for {channel.id} of {user.id} stat {stat}")

        if channel in self._stats_cache.keys():
            if user in self._stats_cache[channel]:
                return self._stats_cache[channel][user][stat]
        else:
            self._stats_cache[channel] = {}

        await self.ensure_gamer_exist(channel, user)

        res = await self.request_json(self.gamers_endpoint + f'{channel.id}/{user.id}/')

        self._stats_cache[channel][user] = res
        value = res[stat]

        return value

    async def set_stat(self, channel, user, stat, value):
        await self.set_stats(channel, user, {stat: value})

    async def set_stats(self, channel, user, data):
        # self.bot.logger.debug(f"set_stat for {channel.id} of {user.id} stat {stat} with value {value}")
        cond = data.get("exp") and await self.get_pref(channel.guild, "announce_level_up")
        if cond:
            ancien_niveau = await self.get_level(channel=channel, player=user)

        await self.ensure_gamer_exist(channel, user)

        # self.bot.logger.debug(f"> In the DB, the channel is {channel_id}")
        self.bot.logger.debug(f"-> (set_stats) {user.id}")
        headers = self.headers
        async with aiohttp.ClientSession() as cs:
            async with cs.patch(self.gamers_endpoint + f'{channel.id}/{user.id}/', data=data, headers=headers) as r:
                res = (await r.json())[:75]
                self.bot.logger.debug(f"<- ({r.status}) {res}")

        if channel in self._stats_cache.keys():
            if user in self._stats_cache[channel]:
                self._stats_cache[channel].pop(user)
        else:
            self._stats_cache[channel] = {}

        ## LEVEL UP EMBEDS ##
        if cond:
            level = await self.get_level(channel=channel, player=user)

            _ = self.bot._
            language = await self.get_pref(channel.guild, "language")

            embed = discord.Embed(description=_("Level of {player} on #{channel}", language).format(**{"player": user.name, "channel": channel.name}))

            if ancien_niveau["niveau"] > level["niveau"]:
                embed.title = _("You leveled down!", language)
                embed.colour = discord.Colour.red()
            elif ancien_niveau["niveau"] < level["niveau"]:
                embed.title = _("You leveled up!", language)
                embed.colour = discord.Colour.green()
            else:
                return

            embed.set_thumbnail(url=user.avatar_url if user.avatar_url else self.bot.user.avatar_url)
            embed.url = 'https://duckhunt.me/'

            embed.add_field(name=_("Current level", language), value=str(level["niveau"]) + " (" + _(level["nom"], language) + ")")
            embed.add_field(name=_("Previous level", language), value=str(ancien_niveau["niveau"]) + " (" + _(ancien_niveau["nom"], language) + ")")
            embed.add_field(name=_("Shots accuracy", language), value=str(level["precision"]))
            embed.add_field(name=_("Weapon reliability", language), value=str(level["fiabilitee"]))
            embed.add_field(name=_("Exp points", language), value=str(await self.get_stat(channel, user, "exp")))
            embed.set_footer(text='DuckHunt V3', icon_url='http://api-d.com/snaps/2016-11-19_10-38-54-q1smxz4xyq.jpg')
            try:
                await self.bot.send_message(where=channel, embed=embed)
            except:
                await self.bot.send_message(where=channel,
                                            message=_(":warning: There was an error while sending the embed, please check if the bot has the `embed_links` permission and try again!", language))

    async def delete_stats(self, channel, user: discord.Member = None, user_id: int = None):
        if user and not user_id:
            user_id = user.id
        elif user and user_id:
            raise AssertionError(f"Too many arguments passed : user = {user}, user_id = {user_id}")

        self.bot.logger.debug(f"Delete_stats in {channel.id} of {user_id}")

        if channel in self._stats_cache.keys():
            self._stats_cache[channel] = {}

        # self.bot.logger.debug(f"> In the DB, the channel is {channel_id}")

        await self.bot.log(level=5, title="User stats deleted", message=f"The channel statistics of {user_id} have been deleted", where=channel)

        async with aiohttp.ClientSession() as cs:
            async with cs.delete(self.gamers_endpoint + f'{channel.id}/{user_id}/', headers=self.headers) as r:
                pass

    async def delete_channel_stats(self, channel):
        self.bot.logger.debug(f"Delete_channel_stats in {channel.id}")
        await self.bot.log(level=6, title="Channel stats deleted", message=f"The channel statistics have been reinitialised", where=channel)

        async with aiohttp.ClientSession() as cs:
            async with cs.delete(self.channels_endpoint + f'{channel.id}/', headers=self.headers) as r:
                res = (await r.json())[:75]
                self.bot.logger.debug(f"<- ({r.status}) {res}")

        if channel in self._stats_cache.keys():
            self._stats_cache[channel] = {}

    async def add_to_stat(self, channel, user, stat: str, to_add: int):
        await self.set_stat(channel, user, stat, await self.get_stat(channel, user, stat) + to_add)

    # > Prefs < #
    async def get_pref(self, channel, pref):

        if isinstance(channel, discord.Guild):
            raise Exception("Guild used in place of channel")
        if channel in self._settings_cache.keys():
            return await self._settings_cache[channel][pref]

        await self.enable_channel(channel)

        # #self.bot.logger.debug(f"get_pref for {guild.id} pref {pref}")

        res = await self.request_json(self.channels_endpoint + f'{channel.id}/')
        self.bot.logger.debug(res)
        self._settings_cache[channel] = res
        value = res[pref]
        return value

    async def set_pref(self, channel, pref, value):
        if isinstance(channel, discord.Guild):
            raise Exception("Guild used in place of channel")
        if channel in self._settings_cache.keys():
            self._settings_cache.pop(channel)

        await self.ensure_channel_exist(channel)

        self.bot.logger.debug(f"-> (set_pref) {channel.id}, {pref}, {value}")
        headers = self.headers
        async with aiohttp.ClientSession() as cs:
            async with cs.patch(self.channels_endpoint + f'{channel.id}/', data={pref: value}, headers=headers) as r:
                res = (await r.json())[:75]
                self.bot.logger.debug(f"<- ({r.status}) {res}")

        await self.bot.log(level=2, title="Setting changed", message=f"{pref} now set to {value}", where=channel)

    # > Admins < #

    async def get_admins(self, guild):
        return []

    async def add_admin(self, guild, user):
        return False

    async def del_admin(self, guild, user):
        return False


def setup(bot):
    bot.db = Database(bot)
