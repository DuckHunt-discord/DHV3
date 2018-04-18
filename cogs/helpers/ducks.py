"""
In this helper, every kind of duck the bot can spawn is defined.
"""
import logging
import random
import time


class BaseDuck:
    """
    Just a dummy duck type to highlight the required values a Duck subclass must provide
    """

    def __init__(self, bot, channel):

        self.bot = bot
        self.channel = channel

        self._logger = None

        self.starting_life = 1
        self.life = 1

        self.spawned_at = int(time.time())

        # Optional settings that probably won't get changed often
        self.can_miss = True
        self.can_use_clover = True

        # Dummy values that should be replaced... Probably
        self.exp_value = 0
        self.staying_until = self.spawned_at
        self.discord_spawn_str = "-,_,.-'\`'°-,_,.-'\`'° \\_O< COIN"
        self.discord_leave_str = "·°'\`'°-.,¸¸.·°'\`"

        self.logger.warning(f"BAD Duck created -> {self}")
    @property
    def logger(self):
        if not self._logger:
            extra = {"channelid": self.channel.id, "userid": 0}
            self._logger = logging.LoggerAdapter(self.bot.base_logger, extra)

        return self._logger

    @property
    def is_super_duck(self):
        self.bot.logger.warning("Deprecation warning : is_super_duck used")
        return self.type == 1

    @property
    def killed(self):
        if self.life <= 0:
            return True
        else:
            return False

    @property
    def time(self):
        return self.spawned_at

    @classmethod
    async def create(self, bot, channel, ignore_event=False):
        raise RuntimeError("Trying to create an instance of BaseDuck, or subclass not re-implementing create")

    async def get_frighten_chance(self):
        return await self.bot.db.get_pref(self.channel.guild, "duck_frighten_chance")

    async def get_killed_string(self):
        _ = self.bot._
        language = await self.bot.db.get_pref(self.channel.guild, "language")

        return _(":skull_crossbones: **{onomatopoeia}**\tYou killed the duck in {time} seconds, you are now at a grand total of {total} ducks (of which {supercanards} "
                 "were super-ducks) killed on #{channel}.     \_X<   *COUAC*   {exp}", language)

    async def get_harmed_message(self):
        _ = self.bot._
        language = await self.bot.db.get_pref(self.channel.guild, "language")

        if await self.bot.db.get_pref(self.channel.guild, "show_super_ducks_life"):
            return _(":gun: The duck survived, try again! *SUPER DUCK DETECTED* [life: -{vie} ({current_life} / {max_life})]", language)
        else:
            return _(":gun: The duck survived, try again! *SUPER DUCK DETECTED* [life: -{vie}]", language)

    def __repr__(self):
        now = int(time.time())
        return f"Bad BASE DUCK spawned {now - self.spawned_at} seconds ago on #{self.channel.name}"

    def __str__(self):
        now = int(time.time())
        return f"Bad BASE DUCK spawned {now - self.spawned_at} seconds ago on #{self.channel.name}"


class Duck(BaseDuck):
    """
    The common duck, with a life of one that can spawn in the game
    """

    def __init__(self, bot, channel, exp, ttl):
        super().__init__(bot, channel)

        self.staying_until = self.spawned_at + ttl
        self.exp_value = exp
        self.logger.debug(f"Duck created -> {self}")

    def __repr__(self):
        now = int(time.time())

        return f"Duck spawned {now - self.spawned_at} seconds ago on {self.channel.id}. " \
               f"Exp value of {self.exp_value}"

    def __str__(self):
        now = int(time.time())
        return f"Duck spawned {now - self.spawned_at} seconds ago on #{self.channel.name} @ {self.channel.guild.name} " \
               f"Exp value of {self.exp_value}"

    async def _gen_discord_str(self):
        _ = self.bot._
        language = await self.bot.db.get_pref(self.channel.guild, "language")

        if await self.bot.db.get_pref(self.channel.guild, "emoji_ducks"):
            corps = await self.bot.db.get_pref(self.channel.guild, "emoji_used") + " < "
        else:
            corps = random.choice(self.bot.canards_trace) + "  " + random.choice(self.bot.canards_portrait) + "  "

        if await self.bot.db.get_pref(self.channel.guild, "randomize_ducks"):
            canard_str = corps + _(random.choice(self.bot.canards_cri), language=language)
        else:
            canard_str = corps + "QUAACK"

        self.discord_spawn_str = canard_str
        self.discord_leave_str = _(random.choice(self.bot.canards_bye), language)

    @classmethod
    async def create(cls, bot, channel, ignore_event=False):

        # Base duck time to live
        ttl = await bot.db.get_pref(channel.guild, "time_before_ducks_leave")

        # Base duck exp
        exp_value = await bot.db.get_pref(channel.guild, "exp_won_per_duck_killed")

        duck = cls(bot, channel, exp=exp_value, ttl=ttl)
        await duck._gen_discord_str()
        return duck


class SuperDuck(BaseDuck):
    """
    A special duck with more than one life point
    """

    def __init__(self, bot, channel, life, exp, ttl):
        super().__init__(bot, channel)
        self.staying_until = self.spawned_at + ttl
        self.exp_value = exp

        self.life = life
        self.starting_life = life
        self.logger.debug(f"Duck created -> {self}")


    def __repr__(self):
        now = int(time.time())
        return f"Super Duck spawned {now - self.spawned_at} seconds ago on #{self.channel.name}" \
               f"Life: {self.life} / {self.starting_life}, and an exp value of {self.exp_value}"

    def __str__(self):
        now = int(time.time())
        return f"Super Duck spawned {now - self.spawned_at} seconds ago on #{self.channel.name} @ {self.channel.guild.name} " \
               f"Life: {self.life} / {self.starting_life}, and an exp value of {self.exp_value}"

    async def _gen_discord_str(self):
        _ = self.bot._
        language = await self.bot.db.get_pref(self.channel.guild, "language")

        if await self.bot.db.get_pref(self.channel.guild, "emoji_ducks"):
            corps = await self.bot.db.get_pref(self.channel.guild, "emoji_used") + " < "
        else:
            corps = random.choice(self.bot.canards_trace) + "  " + random.choice(self.bot.canards_portrait) + "  "

        if await self.bot.db.get_pref(self.channel.guild, "randomize_ducks"):
            canard_str = corps + _(random.choice(self.bot.canards_cri), language=language)
        else:
            canard_str = corps + "QUAACK"

        self.discord_spawn_str = canard_str
        self.discord_leave_str = _(random.choice(self.bot.canards_bye), language)


    @classmethod
    async def create(cls, bot, channel, ignore_event=False):
        # Base duck time to live
        ttl = await bot.db.get_pref(channel.guild, "time_before_ducks_leave")

        # Base duck exp
        exp_value = await bot.db.get_pref(channel.guild, "exp_won_per_duck_killed")

        # Super duck life
        min_life = await bot.db.get_pref(channel.guild, "super_ducks_minlife")
        max_life = await bot.db.get_pref(channel.guild, "super_ducks_maxlife")

        # Choosen life for this one
        life = random.randint(min(min_life, max_life), max(min_life, max_life))
        if not ignore_event and bot.current_event['id'] == 7:
            life += bot.current_event['life_to_add']

        # Choosen exp for this life
        exp_value = int(exp_value * await bot.db.get_pref(channel.guild, "super_ducks_exp_multiplier") * life)

        duck = cls(bot, channel, life=life, exp=exp_value, ttl=ttl)
        await duck._gen_discord_str()

        return duck


class MechanicalDuck(BaseDuck):
    """
    Special duck "already killed" just to troll other hunters
    """

    def __init__(self, bot, channel, ttl=30):
        super().__init__(bot, channel)
        self.life = 1
        self.exp_value = -1
        self.staying_until = self.spawned_at + ttl
        self.user = None
        self.can_miss = False
        self.can_use_clover = False
        self.logger.debug(f"Duck created -> {self}")

    @property
    def user_name(self):
        if self.user:
            return self.user.name + "#" + self.user.discriminator
        else:
            return None

    @property
    def user_mention(self):
        if self.user:
            return self.user.mention
        else:
            return None


    async def _gen_discord_str(self):
        _ = self.bot._
        language = await self.bot.db.get_pref(self.channel.guild, "language")
        guild = self.channel.guild

        if await self.bot.db.get_pref(self.channel.guild, "emoji_ducks"):
            if await self.bot.db.get_pref(guild, "randomize_mechanical_ducks") == 0:
                canard_str = await self.bot.db.get_pref(guild, "emoji_used") + _(" < *BZAACK*", language)
            else:
                canard_str = _(await self.bot.db.get_pref(guild, "emoji_used") + " < " + _(random.choice(self.bot.canards_cri), language))
        else:
            if await self.bot.db.get_pref(guild, "randomize_mechanical_ducks") == 0:
                canard_str = _("-_-'\`'°-_-.-'\`'° %__%   *BZAACK*", language)
            elif await self.bot.db.get_pref(guild, "randomize_mechanical_ducks") == 1:
                canard_str = _("-_-'\`'°-_-.-'\`'° %__%    " + _(random.choice(self.bot.canards_cri), language))
            else:
                canard_str = random.choice(self.bot.canards_trace + "  " + random.choice(self.bot.canards_portrait) + "  " + _(random.choice(self.bot.canards_cri), language))  # ASSHOLE ^^

        self.discord_spawn_str = canard_str
        self.discord_leave_str = None

    @classmethod
    async def create(cls, bot, channel, ignore_event=False, user=None):
        duck = cls(bot, channel)
        duck.user = user
        await duck._gen_discord_str()
        return duck

    async def get_killed_string(self):
        _ = self.bot._
        language = await self.bot.db.get_pref(self.channel.guild, "language")

        return _("You have been tricked by {user_mention} to kill a mechanical duck. It obviouly won't work, and you lost 1 exp for this missed shot", language).format(user_mention = self.user_mention)


    async def get_frighten_chance(self):
        return 0

    def __repr__(self):
        now = int(time.time())
        return f"Mechanical Duck spawned {now - self.spawned_at} seconds ago on #{self.channel.name}" \
               f"Made by {self.user_name}"

    def __str__(self):
        now = int(time.time())
        return f"Mechanical Duck spawned {now - self.spawned_at} seconds ago on #{self.channel.name}" \
               f"Made by {self.user_name}"
