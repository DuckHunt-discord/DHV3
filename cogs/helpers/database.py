import discord
import records

# How to migrate from DH-V2
# 1/ Create tables prefs and admins
# 2/ Add enabled column to channels
import sqlalchemy
import time


class Database:

    def __init__(self, bot):
        self.bot = bot
        # Create the database object
        self.database = records.Database(f'mysql+mysqlconnector://{bot.database_user}:{bot.database_password}'
                                         f'@{bot.database_address}:{bot.database_port}'
                                         f'/{bot.database_name}?charset=utf8mb4')
        self.recreate_caches()

    def recreate_caches(self):
        self._settings = []
        self._settings_full = []
        self._channel_dbid_cache = {}
        self._channel_enabled_cache = {}
        self._settings_dict = None
        self._settings_cache = {}
        self._stats_cache = {}

    # > Channels <

    async def get_channel_dbid(self, channel):
        # okay, so first, we'll have to find the channel id in the database.
        # For this, we can query duckhunt/channels with the right guild+channel id combo,
        # and we will get the ID we need

        if channel in self._channel_dbid_cache.keys():
            return self._channel_dbid_cache[channel]
        else:

            row = self.database.query("SELECT id, channel_name FROM channels WHERE server=:server_id AND channel=:channel_id "
                                      "LIMIT 1;", server_id=channel.guild.id, channel_id=channel.id)

            if row.first():
                id_ = row.first().id
                self._channel_dbid_cache[channel] = id_

                if channel.name != row.first().channel_name:
                    self.database.query("UPDATE channels SET channel_name = :channel_name WHERE id=:id", id=id_, channel_name=channel.name)
                return id_
            else:
                return None

    async def channel_is_enabled(self, channel):
        if channel in self._channel_enabled_cache.keys():
            return self._channel_enabled_cache[channel]

        row = self.database.query("SELECT enabled FROM channels WHERE server=:server_id AND channel=:channel_id "
                                  "LIMIT 1;", server_id=channel.guild.id, channel_id=channel.id)
        if row.first():
            res = bool(row.first().enabled)
            self._channel_enabled_cache[channel] = res
            return res
        else:
            return False  # If the channel is not in the DB, it's not enabled

    async def enable_channel(self, channel):
        self.database.query("INSERT INTO channels (server, channel, enabled) VALUES (:server_id, :channel_id, 1) "
                            "ON DUPLICATE KEY UPDATE enabled=1", server_id=channel.guild.id, channel_id=channel.id)
        self._channel_enabled_cache[channel] = True
        await self.bot.log(level=5, title="Channel enabled", message=f"The channel is now active", where=channel)
        if channel in self._stats_cache.keys():
            self._stats_cache[channel] = {}

    async def disable_channel(self, channel):
        self.database.query("INSERT INTO channels (server, channel, enabled) VALUES (:server_id, :channel_id, 0) "
                            "ON DUPLICATE KEY UPDATE enabled=0", server_id=channel.guild.id, channel_id=channel.id)
        self._channel_enabled_cache[channel] = False
        await self.bot.log(level=5, title="Channel disabled", message=f"The channel is now disabled", where=channel)
        if channel in self._stats_cache.keys():
            self._stats_cache[channel] = {}

    async def list_enabled_channels(self):
        row = self.database.query("SELECT channel, server FROM channels WHERE enabled=1")
        return row.all()

    async def get_all_admins_ids(self):
        row = self.database.query("SELECT DISTINCT `user_id` from admins")
        return [int(r.user_id) for r in row.all()]

    # > Stats < #

    async def top_scores(self, channel, sorted_by, second_sort_by):
        channel_id = await self.get_channel_dbid(channel)
        reverse_list = ["exp", "killed_ducks"]
        if sorted_by in reverse_list:
            sorted_by = f"{sorted_by} DESC"

        if second_sort_by in reverse_list:
            second_sort_by = f"{second_sort_by} DESC"
        row = self.database.query(f"SELECT * FROM players WHERE channel_id=:channel_id AND (exp <> 0 OR killed_ducks > 0) ORDER BY {sorted_by}, {second_sort_by}", channel_id=channel_id)

        return row.all()

    async def get_level(self, exp=None, channel=None, player=None):
        levels = self.bot.players_levels

        if not exp:
            exp = await self.get_stat(channel, player, "exp")

        # From https://stackoverflow.com/a/7125547
        # Cherche le "dernier" element de levels qui satifie la condition expMin <= exp

        return next((level for level in reversed(levels) if level["expMin"] <= exp), levels[0])

    async def giveback(self, channel, user):

        # self.bot.logger.debug(f"giveback for {channel.id} of {user.id}")
        channel_id = await self.get_channel_dbid(channel)
        # self.bot.logger.debug(f"> In the DB, the channel is {channel_id}")

        level = await self.get_level(channel=channel, player=user)

        self.database.query("INSERT INTO players (id_, channel_id, chargeurs, balles, confisque, lastGiveback, givebacks) "
                            "VALUES (:id_, :channel_id, :chargeurs, :balles, 0, :now, 1) "
                            "ON DUPLICATE KEY UPDATE chargeurs = :chargeurs, "
                            "confisque = 0,lastGiveback = :now, givebacks=givebacks+1",

                            id_=user.id, channel_id=channel_id, chargeurs=level["chargeurs"], balles=level["balles"], now=int(time.time()))

        if channel in self._stats_cache.keys():
            if user in self._stats_cache[channel]:
                self._stats_cache[channel].pop(user)
        else:
            self._stats_cache[channel] = {}

    async def get_stat(self, channel, user, stat: str):
        # self.bot.logger.debug(f"get_stat for {channel.id} of {user.id} stat {stat}")

        if channel in self._stats_cache.keys():
            if user in self._stats_cache[channel]:
                return self._stats_cache[channel][user][stat]
        else:
            self._stats_cache[channel] = {}

        channel_id = await self.get_channel_dbid(channel)
        # self.bot.logger.debug(f"> In the DB, the channel is {channel_id}")

        row = None
        while not row:
            # Now that we have the ID, we can get into duckhunt/players and find the player we need
            row = self.database.query("SELECT * FROM players WHERE channel_id=:channel_id AND id_=:user_id LIMIT 1;", stat=stat, channel_id=channel_id, user_id=user.id)

            if row.first() is None:
                # Wasn't in the DB
                self.database.query("INSERT INTO players (id_, channel_id, name) VALUES (:user_id, :channel_id, :name_)", channel_id=channel_id, user_id=user.id,
                                    name_=user.name + "#" + user.discriminator)

        row = row.first()
        # self.bot.logger.debug(f"> Value : {value}")

        self._stats_cache[channel][user] = row
        value = row[stat]

        return value

    async def set_stat(self, channel, user, stat: str, value: int):
        # self.bot.logger.debug(f"set_stat for {channel.id} of {user.id} stat {stat} with value {value}")
        cond = stat == "exp" and await self.get_pref(channel.guild, "announce_level_up")
        if cond:
            ancien_niveau = await self.get_level(channel=channel, player=user)

        channel_id = await self.get_channel_dbid(channel)
        # self.bot.logger.debug(f"> In the DB, the channel is {channel_id}")

        # Now that we have the ID, we can get into duckhunt/players and update the player we need
        self.database.query(f"INSERT INTO players (channel_id, id_, name, avatar_url, {stat}) VALUES (:channel_id, :user_id, :name_, :avatar_url, :stat_value) "
                            f"ON DUPLICATE KEY UPDATE {stat} = :stat_value, name=:name_, avatar_url=:avatar_url", channel_id=channel_id, user_id=user.id, stat_value=value,
                            avatar_url=user.avatar_url_as(static_format='jpg', size=1024), name_=user.name + "#" +
                                                                                                                                                                      user.discriminator)

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

        channel_id = await self.get_channel_dbid(channel)
        # self.bot.logger.debug(f"> In the DB, the channel is {channel_id}")

        await self.bot.log(level=5, title="User stats deleted", message=f"The channel statistics of {user_id} have been deleted", where=channel)
        self.database.query(f"DELETE FROM players WHERE channel_id=:channel_id AND id_=:user_id", channel_id=channel_id, user_id=user_id)

    async def delete_channel_stats(self, channel):
        self.bot.logger.debug(f"Delete_channel_stats in {channel.id}")
        channel_id = await self.get_channel_dbid(channel)
        await self.bot.log(level=6, title="Channel stats deleted", message=f"The channel statistics have been reinitialised", where=channel)

        self.database.query(f"DELETE FROM players WHERE channel_id=:channel_id", channel_id=channel_id)

        if channel in self._stats_cache.keys():
            self._stats_cache[channel] = {}

    async def add_to_stat(self, channel, user, stat: str, to_add: int):
        await self.set_stat(channel, user, stat, await self.get_stat(channel, user, stat) + to_add)

    # > Prefs < #

    @property
    def settings_list(self):
        if not self._settings_full:
            row = self.database.query("DESCRIBE prefs;")

            self._settings_full = row.all()

        return [r.Field for r in self._settings_full]

    @property
    def settings(self):
        if not self._settings_full:
            row = self.database.query("DESCRIBE prefs;")

            self._settings_full = row.all()

        return self._settings_full

    @property
    def settings_dict(self):

        if not self._settings_dict:
            self._settings_dict = {x["Field"]: x.as_dict() for x in self.settings}

        return self._settings_dict

    async def format_value(self, setting, value):
        type_ = setting["Type"]
        if type_.startswith("int"):
            value = int(value)
        elif type_.startswith("tinyint(1)"):
            value = self.bool_(value)
        elif type_.startswith("tinyint"):
            value = int(value)
        elif type_.startswith("smallint"):
            value = int(value)
        elif type_.startswith("float"):
            value = float(value)
        elif type_.startswith("varchar") or type_.startswith("char"):
            value = str(value)
        else:
            self.bot.logger.warning(f"The type {type_} is unknown to me in {setting}. Passing not modified value.")
        return value

    async def get_pref(self, guild, pref):
        try:
            setting = self.settings_dict[pref]
        except KeyError:
            self.bot.logger.exception("An invalid pref have been passed to get pref. THIS SHOULDN'T HAPPEN")
            return False

        if guild in self._settings_cache.keys():
            return await self.format_value(setting, self._settings_cache[guild][pref])


        # #self.bot.logger.debug(f"get_pref for {guild.id} pref {pref}")

        # TODO : Optimize to select mypref from prefs

        row = self.database.query("SELECT * FROM prefs WHERE server_id=:guild_id LIMIT 1;", guild_id=guild.id)

        if row.first():
            row = row.first()
            self._settings_cache[guild] = row
            value = row[pref]


            return await self.format_value(setting, value)
        else:
            assert isinstance(guild, discord.Guild)
            self.bot.logger.info(f"Adding server {guild.id} ({guild.name}) to the prefs database")
            # The guild wasn't created in the DB yet.
            self.database.query("INSERT INTO prefs (server_id) VALUES (:guild_id)", guild_id=guild.id)
            return await self.get_pref(guild, pref)  # Return the pref now

    def bool_(self, b):
        return str(b).lower() in ['true', '1', 't', 'y', 'yes', 'yeah', 'yep', 'yup', 'absolutely', 'certainly', 'definitely', 'uh-huh', 'ouais', 'oui', 'ok', 'on', 'vrai', 'ye', 'actif']

    async def set_pref(self, guild, pref, value):
        try:
            setting = self.settings_dict[pref]
        except KeyError:
            self.bot.logger.exception("An invalid pref have been passed to set pref. THIS SHOULDN'T HAPPEN")
            return False

        # self.bot.logger.debug(f"set_pref for {guild.id} pref {pref} with value {value}")

        value = await self.format_value(setting, value)

        if guild in self._settings_cache.keys():
            self._settings_cache.pop(guild)

        try:
            self.database.query(f"INSERT INTO prefs (server_id, {pref}) VALUES (:server_id, :value)"
                                f"ON DUPLICATE KEY UPDATE {pref}=:value", value=value, server_id=guild.id)
            await self.bot.log(level=2, title="Setting changed", message=f"{pref} now set to {value}", where=guild)

            return True
        except Exception as e:
            self.bot.logger.exception(f"Something bag happened when setting a pref : {e}")
            return False

    # > Admins < #

    async def get_admins(self, guild):
        # #self.bot.logger.debug(f"get_admins for {guild.id}")

        row = self.database.query("SELECT user_id FROM admins WHERE server_id=:guild_id", guild_id=guild.id)

        return [r.user_id for r in row.all()]

    async def add_admin(self, guild, user):
        # self.bot.logger.debug(f"add_admin for {guild.id} and user {user.id}")

        try:
            self.database.query("INSERT INTO admins (server_id, user_id) VALUES (:guild_id, :user_id)", guild_id=guild.id, user_id=user.id)
            await self.bot.log(level=6, title="Admin added to a guild", message=f"{user.name}#{user.discriminator} is now an admin of this guild", where=guild)
            return True
        except sqlalchemy.exc.IntegrityError:  # user is admin already
            return False

    async def del_admin(self, guild, user):
        # self.bot.logger.debug(f"del_admin for {guild.id} and user {user.id}")

        self.database.query("DELETE FROM admins WHERE server_id=:guild_id AND user_id=:user_id", guild_id=guild.id, user_id=user.id)


def setup(bot):
    bot.db = Database(bot)
